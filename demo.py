import subprocess
import time
import serial

# Hàm chạy lệnh main_app như trước
def cmd(option):
    try:
        result = subprocess.run(["./main_app", option], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {option}")
        else:
            print(f"✗ {option} failed")
    except Exception as e:
        print(f"Error running {option}: {e}")


# Hàm gửi lệnh qua UART và chờ nhận "OK"
def send_direction1_command(ser, command, timeout=20):
    ser.write((command + "\n").encode())  # Gửi lệnh, kèm newline nếu cần
    ser.flush()
    print(f"> Sent: {command}")

    start_time = time.time()
    received = ""

    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            print(f"< Received: {line}")
            received += line
            if "OK" in line:
                return True
        time.sleep(0.1)

    print("Timeout waiting for OK response.")
    return False


if __name__ == "__main__":
    # Mở cổng serial, điều chỉnh port + baudrate theo thiết bị của bạn
    try:
        ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
        print("UART opened.")
    except Exception as e:
        print(f"Failed to open UART: {e}")
        ser = None

    print("Starting LED blink loop (Ctrl+C to stop)...")
    print("=" * 40)

    try:
        print("Reflashing the device...")
        cmd("--Reflash")

        while True:
            print("Sending direction1 command and waiting for OK...")
            if ser:
                if send_direction1_command(ser, "direction1: command"):
                    print("Received OK from device.")
                else:
                    print("Did not receive OK.")

            print("Sys On...")
            cmd("--Sys_On")
            time.sleep(1)

            print("S Off...")
            cmd("--Sys_Off")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nLED blink stopped!")
        print("Turning LED off...")
        cmd("--Led_Off")
        if ser:
            ser.close()
        print("Done!")
