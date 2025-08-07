import subprocess
import time

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

        print(" S Off...")
        cmd("--Sys_Off")
        time.sleep(1)
        
        
        
except KeyboardInterrupt:
    print("\n\n LED blink stopped!")
    print("Turning LED off...")
    cmd("--Led_Off")  # Make sure LED is off when exiting
    print("Done!")
