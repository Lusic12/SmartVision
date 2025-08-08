import cv2
import time

def test_laptop_camera():
    print("Testing laptop camera...")
    
    # Laptop thường có camera tích hợp ở video0
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera - trying other devices...")
        # Thử camera USB nếu có (video1, video2)
        for i in range(1, 4):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Found camera at device {i}")
                break
        else:
            print("No camera found!")
            return False
    
    # Cài đặt độ phân giải tốt cho laptop
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Lấy thông tin camera
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✓ Camera opened successfully!")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    print("Press 'q' to quit, 's' to screenshot, 'r' to record")
    
    # Biến để ghi video
    recording = False
    video_writer = None
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error reading frame")
            break
        
        frame_count += 1
        
        # Thêm text hiển thị trạng thái
        status_text = f"Frame: {frame_count}"
        if recording:
            status_text += " [RECORDING]"
        
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Hiển thị frame
        cv2.imshow('Laptop Camera Test', frame)
        
        # Xử lý phím nhấn
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Chụp ảnh
            filename = f"laptop_photo_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved: {filename}")
        elif key == ord('r'):
            # Bắt đầu/dừng ghi video
            if not recording:
                video_filename = f"laptop_video_{int(time.time())}.avi"
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, (width, height))
                recording = True
                print(f"Started recording: {video_filename}")
            else:
                recording = False
                if video_writer:
                    video_writer.release()
                    video_writer = None
                print("Recording stopped")
        
        # Ghi frame nếu đang record
        if recording and video_writer:
            video_writer.write(frame)
    
    # Cleanup
    cap.release()
    if video_writer:
        video_writer.release()
    cv2.destroyAllWindows()
    
    print(f"Camera test completed! Total frames: {frame_count}")
    return True

if __name__ == "__main__":
    test_laptop_camera()
