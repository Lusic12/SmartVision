import subprocess
import random
import time

# Hàm chạy lệnh main_app và kiểm tra thành công (giả sử returncode == 0 là "Ok")
def cmd(option):
    try:
        result = subprocess.run(["./main_app", option], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {option} - Response: Ok (success)")
            return True
        else:
            print(f"✗ {option} failed - Response: Fail (error code {result.returncode})")
            return False
    except Exception as e:
        print(f"Error running {option}: {e}")
        return False

# Các command cho Direction
directions = ["--Direction1", "--Direction2", "--Direction3"]

# Array random cho Direction (ký tự '1', '2', '3')
direction_array = []

print("Starting full function demo for UP4000...")
print("=" * 40)

# Test chức năng Reflash đầu tiên
print("Testing --Reflash...")
cmd("--Reflash")

# Test LED On/Off
print("Testing LED functions...")
if cmd("--Led_On"):
    time.sleep(1)
    cmd("--Led_Off")
else:
    print("LED test failed, stopping early.")
    cmd("--Stop_System")
    exit()

# Test Send_Status
print("Testing --Send_Status...")
if not cmd("--Send_Status"):
    print("Send_Status failed, stopping.")
    cmd("--Stop_System")
    exit()

# Vòng lặp chính: Thêm random vào array mỗi 5 giây, rồi test toàn bộ array với Direction
print("Starting Direction random loop (Ctrl+C to stop)...")
try:
    while True:
        # Thêm ký tự random vào array mỗi 5 giây
        time.sleep(5)
        new_char = random.choice(['1', '2', '3'])
        direction_array.append(new_char)
        print(f"New char '{new_char}' added. Current array: {direction_array}")

        # Gửi lệnh cho toàn bộ array
        all_ok = True
        for char in direction_array:
            idx = int(char) - 1  # '1' -> 0, '2' -> 1, '3' -> 2
            command = directions[idx]
            print(f"Testing {command} for char '{char}'...")
            if not cmd(command):
                all_ok = False
                break  # Dừng nếu bất kỳ lệnh nào thất bại

        if not all_ok:
            print("Failed to receive Ok for a Direction command. Stopping system...")
            cmd("--Stop_System")
            break  # Dừng vòng lặp

        print("All Directions Ok, continuing loop...")

except KeyboardInterrupt:
    print("\nDemo stopped by user!")
    cmd("--Led_Off")  # Tắt LED nếu cần
    cmd("--Stop_System")  # Dừng hệ thống khi thoát

print("Demo completed!")
