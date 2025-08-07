import subprocess
import time
import serial

# Simple function to run main_app commands
def cmd(option):
    try:
        result = subprocess.run(["./main_app", option], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {option}")
        else:
            print(f"✗ {option} failed")
    except Exception as e:
        print(f"Error running {option}: {e}")

print("Starting LED blink loop (Ctrl+C to stop)...")
print("=" * 40)

try:
    print("Reflashing the device...")
    cmd("--Reflash")
    while True:
        print(" Sys On...")
        cmd("--Sys_On")
        time.sleep(1)

        print(" Sys Off...")
        cmd("--Sys_Off")
        time.sleep(1)

        print(" Send Direction2...")
        cmd("--Direction2")
        try:
            with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
                start_time = time.time()
                received_ok = False
                while time.time() - start_time < 5:
                    if ser.in_waiting:
                        uart_data = ser.readline().decode('utf-8', errors='ignore').strip()
                        print(f" UART Received: {uart_data}")
                        if uart_data == "OK":
                            received_ok = True
                            break
                    time.sleep(0.1)
                if not received_ok:
                    print("Timeout: Did not receive 'OK' within 5 seconds.")
        except Exception as e:
            print(f"UART error: {e}")

except KeyboardInterrupt:
    print("\n\n LED blink stopped!")
    print("Turning LED off...")
    cmd("--Led_Off")  # Make sure LED is off when exiting
    print("Done!")
