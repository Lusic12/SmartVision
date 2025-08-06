import json
import time
import requests

# ====== CẤU HÌNH THINGSBOARD ======
ACCESS_TOKEN = "MM1iebCrMxSFAZSipZMX"  # Thay bằng token của bạn
THINGSBOARD_URL = "https://demo.thingsboard.io"
POST_URL = f"{THINGSBOARD_URL}/api/v1/{ACCESS_TOKEN}/telemetry"

# ====== CẤU HÌNH FILE JSON ======
JSON_FILE_PATH = r"New folder\shrimp_data.json"

# ====== CHU KỲ GỬI UART DATA ======
UART_SEND_INTERVAL = 300  # gửi mỗi 5 phút (tính bằng giây)
last_uart_send_time = 0

while True:
    try:
        with open(JSON_FILE_PATH, "r") as f:
            data = json.load(f)

        # Timestamp (ThingsBoard yêu cầu timestamp dạng milliseconds)
        timestamp_ms = data.get("timestamp", time.time()) * 1000

        # Dữ liệu chính gửi định kỳ mỗi 5 giây
        telemetry = {
            "ts": int(timestamp_ms),
            "values": {
                "shrimp_total": data.get("shrimp_total", 0),
                "shrimp_current": data.get("shrimp_current", 0),
                "shrimp_small": data.get("shrimp_small", 0),
                "shrimp_medium": data.get("shrimp_medium", 0),
                "shrimp_large": data.get("shrimp_large", 0),
                "shrimp_weight": data.get("shrimp_weight", 0.0),
                "shrimp_total_weight": data.get("shrimp_total_weight", 0.0) 
            }
        }

        # Gửi dữ liệu chính
        response = requests.post(f"{POST_URL}?ts={telemetry['ts']}", json=telemetry["values"])
        print(f"[SEND] {telemetry['values']} | Status: {response.status_code}")

        # Gửi dữ liệu UART (mỗi 5 phút)
        current_time = time.time()
        if current_time - last_uart_send_time >= UART_SEND_INTERVAL:
            uart_telemetry = {
                "ts": int(timestamp_ms),
                "values": {
                    "temperature": data.get("temperature", 0.0),
                    "humidity": data.get("humidity", 0.0)
                }
            }
            uart_response = requests.post(f"{POST_URL}?ts={uart_telemetry['ts']}", json=uart_telemetry["values"])
            print(f"[UART] {uart_telemetry['values']} | Status: {uart_response.status_code}")
            last_uart_send_time = current_time

    except Exception as e:
        print("Lỗi:", e)

    time.sleep(3)
