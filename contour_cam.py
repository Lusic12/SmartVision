import cv2
import numpy as np
import requests

# ThingsBoard
ACCESS_TOKEN = "MM1iebCrMxSFAZSipZMX"  # Thay bằng token thiết bị của bạn
THINGSBOARD_URL = "https://demo.thingsboard.io"
POST_URL = f"{THINGSBOARD_URL}/api/v1/{ACCESS_TOKEN}/telemetry"

# Camera
cap = cv2.VideoCapture(0)

min_area = 3000
max_hole_area = 500
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    original = frame.copy()

    # B1: Tách nền xanh
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_inv = cv2.bitwise_not(mask)

    # B2: Morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask_clean = cv2.morphologyEx(mask_inv, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)

    # B3: Fill lỗ nhỏ
    final_mask = mask_clean.copy()
    contours, hierarchy = cv2.findContours(mask_clean, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is not None:
        for i in range(len(contours)):
            if hierarchy[0][i][3] != -1:
                area = cv2.contourArea(contours[i])
                if area < max_hole_area:
                    cv2.drawContours(final_mask, contours, i, 255, cv2.FILLED)

    # B4: Erosion
    eroded = cv2.erode(final_mask, np.ones((3,3), np.uint8), iterations=1)

    # B5: Distance transform
    dist_transform = cv2.distanceTransform(eroded, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.3 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(final_mask, sure_fg)

    # B6: Watershed
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(original, markers)

    # B7: Đếm
    output = original.copy()
    shrimp_count = 0
    for marker_id in range(2, np.max(markers)+1):
        mask = np.uint8(markers == marker_id)
        mask_full = cv2.bitwise_and(final_mask, final_mask, mask=mask)
        cnts, _ = cv2.findContours(mask_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if area > min_area:
                shrimp_count += 1
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(output, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # B8: Gửi lên ThingsBoard mỗi 5 frame
    if frame_count % 5 == 0:
        try:
            payload = {"shrimp_count": shrimp_count}
            response = requests.post(POST_URL, json=payload, timeout=3)
            print(f"✅ Gửi: {payload} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Lỗi gửi dữ liệu: {e}")

    # Hiển thị lên màn hình
    cv2.putText(output, f"Tong so tom: {shrimp_count}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    cv2.imshow("Real-time Shrimp Detection", output)
    frame_count += 1

    if cv2.waitKey(1) & 0xFF == 27:  # ESC để thoát
        break

cap.release()
cv2.destroyAllWindows()
