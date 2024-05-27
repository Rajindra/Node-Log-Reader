import sys
import serial
import argparse

def main(cmd, outfile, port_suffix):
    serial_port = f'/dev/ttyUSB_{port_suffix}'
    
    with serial.Serial(port=serial_port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, rtscts=0, xonxoff=0) as ser, open(outfile, 'a') as log_file:
        if ser.isOpen():
            print(f'{ser.name} is open.... Please try again')
        
        ser.write((cmd + '\n').encode())

        while True:
            try:
                line = ser.readline()
                if line:
                    log_file.write(line.decode())
                else:
                    break
            except serial.SerialTimeoutException:
                print('Timeout while reading from serial')
                break

        print(f'Log written to file {outfile}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute a command on a serial device and log the output.')
    parser.add_argument('cmd', type=str, help='Command to execute')
    parser.add_argument('-o', '--outputfile', type=str, help='Output file', required=True)
    parser.add_argument('-p', '--port_suffix', type=str, help='Suffix of the serial port (e.g., HPA, HPB, USB1)', required=True)

    args = parser.parse_args()

    main(args.cmd, args.outputfile, args.port_suffix)
