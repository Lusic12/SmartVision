#!/usr/bin/env python3
import subprocess
import time
import serial
import sys
import termios
import tty
from threading import Lock

class InteractiveController:
    def __init__(self, device='/dev/ttyUSB0', baudrate=115200, main_app_path='./main_app'):
        self.device = device
        self.baudrate = baudrate
        self.main_app_path = main_app_path
        self.uart_lock = Lock()
        self.waiting_for_uart = False
        
        # Định nghĩa commands từ main_process.c
        self.commands = {
            '1': {'name': 'Direction1', 'cmd': '--Direction1', 'wait_uart': True},
            '2': {'name': 'Direction2', 'cmd': '--Direction2', 'wait_uart': True},
            '3': {'name': 'Direction3', 'cmd': '--Direction3', 'wait_uart': True},
            '4': {'name': 'Sys_On', 'cmd': '--Sys_On', 'wait_uart': False},
            '5': {'name': 'Sys_Off', 'cmd': '--Sys_Off', 'wait_uart': False},
            '6': {'name': 'Send_Status', 'cmd': '--Send_Status', 'wait_uart': True},
            '7': {'name': 'Stop_System', 'cmd': '--Stop_System', 'wait_uart': False},
            '8': {'name': 'Reflash', 'cmd': '--Reflash', 'wait_uart': True},
            'q': {'name': 'Quit', 'cmd': None, 'wait_uart': False}
        }

    def display_menu(self):
        """Hiển thị menu commands"""
        print("\n" + "="*60)
        print("🎮 INTERACTIVE COMMAND CONTROLLER")
        print("="*60)
        print("📋 Available Commands:")
        print("─"*60)
        
        for key, cmd_info in self.commands.items():
            if key == 'q':
                print(f"   [{key}] ❌ {cmd_info['name']}")
            else:
                uart_status = "🔄 (Wait UART)" if cmd_info['wait_uart'] else "⚡ (Instant)"
                print(f"   [{key}] 🎯 {cmd_info['name']:<15} {uart_status}")
        
        print("─"*60)
        if self.waiting_for_uart:
            print("⏳ Waiting for UART response... Please wait!")
        else:
            print("💡 Select a command [1-8] or [q] to quit:")
        print("="*60)

    def get_key_input(self):
        """Lấy input từ bàn phím không cần Enter"""
        try:
            # Lưu terminal settings cũ
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            # Chuyển sang raw mode
            tty.setraw(sys.stdin.fileno())
            
            # Đọc 1 ký tự
            key = sys.stdin.read(1)
            
            # Khôi phục terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            return key
        except:
            return input().strip().lower()

    def execute_command(self, cmd_option):
        """Thực thi command với main_app"""
        try:
            print(f"\n🔄 Executing: {cmd_option}")
            
            result = subprocess.run(
                [self.main_app_path, cmd_option], 
                capture_output=True, 
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                print(f"✅ Command executed successfully")
                return True
            else:
                print(f"❌ Command failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ Command timeout!")
            return False
        except Exception as e:
            print(f"💥 Error executing command: {e}")
            return False

    def wait_for_uart_response(self, timeout=10):
        """Chờ UART response với timeout"""
        try:
            with serial.Serial(self.device, self.baudrate, timeout=1) as ser:
                print(f"📡 Waiting for UART response (timeout: {timeout}s)...")
                start_time = time.time()
                responses = []
                
                while time.time() - start_time < timeout:
                    if ser.in_waiting:
                        try:
                            data = ser.readline().decode('utf-8', errors='ignore').strip()
                            if data:
                                print(f"📨 UART: {data}")
                                responses.append(data)
                                
                                # Kiểm tra các response hợp lệ
                                if data in ["OK", "DONE", "SUCCESS"]:
                                    print(f"✅ Valid response received: {data}")
                                    return True, responses
                                elif "ERROR" in data.upper():
                                    print(f"❌ Error response: {data}")
                                    return False, responses
                                    
                        except UnicodeDecodeError:
                            continue
                    time.sleep(0.1)
                
                print(f"⏱️ Timeout! No valid response in {timeout}s")
                return False, responses
                
        except serial.SerialException as e:
            print(f"🔌 Serial error: {e}")
            return False, []
        except Exception as e:
            print(f"💥 UART error: {e}")
            return False, []

    def process_command(self, key):
        """Xử lý command được chọn"""
        if key not in self.commands:
            print(f"❌ Invalid command: {key}")
            return True

        cmd_info = self.commands[key]
        
        if key == 'q':
            print("👋 Goodbye!")
            return False

        # Block nếu đang chờ UART
        if self.waiting_for_uart:
            print("⏳ Please wait for UART response before sending new command!")
            return True

        # Thực thi command
        if self.execute_command(cmd_info['cmd']):
            # Nếu command cần chờ UART response
            if cmd_info['wait_uart']:
                self.waiting_for_uart = True
                
                # Chờ UART response
                success, responses = self.wait_for_uart_response()
                
                if success:
                    print("🎉 Command completed successfully!")
                else:
                    print("⚠️ Command executed but no valid UART response")
                
                self.waiting_for_uart = False
            else:
                print("🎉 Command completed!")
        else:
            print("❌ Command execution failed!")
            
        print("\nPress any key to continue...")
        self.get_key_input()
        
        return True

    def run(self):
        """Chạy main loop"""
        print("🚀 Starting Interactive Command Controller...")
        print(f"📱 Device: {self.device}")
        print(f"⚡ Baudrate: {self.baudrate}")
        print(f"🔧 Main App: {self.main_app_path}")
        
        try:
            while True:
                # Clear screen (Linux/Mac)
                subprocess.run(['clear'], check=False)
                
                # Hiển thị menu
                self.display_menu()
                
                # Lấy input từ user
                key = self.get_key_input().lower()
                
                # Xử lý command
                if not self.process_command(key):
                    break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user!")
            print("🔧 Executing cleanup...")
            
            # Cleanup: Turn off system
            try:
                self.execute_command('--Sys_Off')
            except:
                pass
                
            print("✅ Cleanup done!")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")

def main():
    """Main function với argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Interactive Command Controller')
    parser.add_argument('-d', '--device', default='/dev/ttyUSB0',
                       help='UART device path (default: /dev/ttyUSB0)')
    parser.add_argument('-B', '--baudrate', type=int, default=115200,
                       help='UART baudrate (default: 115200)')
    parser.add_argument('--main-app', default='./main_app',
                       help='Path to main_app executable (default: ./main_app)')
    
    args = parser.parse_args()
    
    # Tạo và chạy controller
    controller = InteractiveController(
        device=args.device,
        baudrate=args.baudrate,
        main_app_path=args.main_app
    )
    
    controller.run()

if __name__ == "__main__":
    main()
