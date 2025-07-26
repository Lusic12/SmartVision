#!/bin/bash
# Flash the ESP32 with the binary file
source ../../../esptool-env/bin/activate
esptool --chip esp32 --port /dev/ttyUSB0 write-flash 0x10000 ../dcs-test.bin
deactivate
# Default values
BAUDRATE=${1:-115200}
DEVICE=${2:-/dev/ttyUSB0}

# Init UART
echo "Initializing UART with baudrate $BAUDRATE on $DEVICE..."
./main_app -B$BAUDRATE -d$DEVICE

# Loop to send commands
# while true; do
#     # echo "Sending Direction1..."
#     # ./uart_app --Direction1
#     # sleep 3
#     echo "Sending Direction2..."
#     ./uart_app --Direction2
#     sleep 3
#     # echo "Sending Direction3..."
#     # ./uart_app --Direction3
#     # sleep 3 
#     echo "Sending Led_On..."
#     ./uart_app --Led_On
#     sleep 1
#     echo "Sending Led_Off..."
#     ./uart_app --Led_Off
#     sleep 1
#     echo "Sending Send_Status and reading response..."
#     ./uart_app --Send_Status
#     # Delay 0.5 seconds before next iteration
#     sleep 0.5
# done