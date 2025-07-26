#include "main.h"
#include "control_command.h"

const struct option long_options[] = {
    {"Direction1", no_argument, 0, 0},
    {"Direction2", no_argument, 0, 0},
    {"Direction3", no_argument, 0, 0},
    {"Led_On",     no_argument, 0, 0},
    {"Led_Off",    no_argument, 0, 0},
    {"Send_Status",no_argument, 0, 0},
    {"Stop_System",no_argument, 0, 0},
    {"Reflash",    no_argument, 0, 0},
    {0,            0,           0, 0}
};


int main(int argc, char **argv) {
    int opt;
    int option_index = 0;
    uint32_t baudrate = 115200;  // Default baudrate
    char *device = "/dev/ttyUSB0";  // Default device

    // Try to load saved config
    load_config(&baudrate, &device);
    Uart_Init(map_to_speed(baudrate), device);

    while ((opt = getopt_long(argc, argv, "B:d:", long_options, &option_index)) != -1) {
        switch (opt) {
            case 0:
                switch (option_index) {
                    case 0: // -- Direction1
                        write_command(CMD_DIRECTION_1);
                        break;
                    case 1:  // -- Direction2
                        write_command(CMD_DIRECTION_2);
                        break;
                    case 2:  // -- Direction3
                        write_command(CMD_DIRECTION_3);
                        break;
                    case 3:  // -- Led_On
                        write_command(CMD_LED_ON);
                        break;
                    case 4:  // -- Led_Off
                        write_command(CMD_LED_OFF);
                        break;
                    case 5:  // -- Send_Status
                        write_command(CMD_SEND_STATUS);
                        break;
                    case 6:  // -- Stop_System
                        write_command(CMD_STOP_SYSTEM);
                        break;
                    case 7:  // -- Reflash
                        uint8_t ret = system("bash -c 'source ../../esptool-env/bin/activate && "
                        "esptool --chip esp32 --port /dev/ttyUSB0 write-flash 0x10000 dcs-test.bin && "
                        "deactivate'");
                        Clear_Startup_UART(uart_fd, 10000);
                        break;
                    default:
                        fprintf(stderr, "Unknown long option.\n");
                        exit(1);
                }
                break;
            case 'B':  // -B for baudrate
                baudrate = atoi(optarg);
                if (map_to_speed(baudrate) == B115200) baudrate = 115200; // Ensure valid baudrate
                break;
            case 'd':  // -d for device
                device = optarg;
                break;
            case '?':  // Option not recognized!
                fprintf(stderr, "Usage: ./uart_app [--direction1] [--relay_on] etc. [-B<baud>] [-d<device>]\n");
                exit(1);
            default:
                break;
        }
    }
    close(uart_fd);
    return 0;
}
