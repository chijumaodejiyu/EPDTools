import serial
import time
from typing import Tuple, Optional

class SerialPort:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 10.0):
        """Initialize serial port
        
        Args:
            port: COM port name (e.g. 'COM3')
            baudrate: baud rate (default 115200)
            timeout: communication timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        
    def open(self) -> bool:
        """Open serial connection"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            time.sleep(1)  # Wait for device to initialize
            return True
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            return False
            
    def close(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            
    def send_img_data(self, bw_data: bytes, rw_data: bytes) -> bool:
        """Send image data through serial port
        
        Args:
            bw_data: black/white image data
            rw_data: red/white image data
            
        Returns:
            bool: True if transmission succeeded
        """
        if not self.ser or not self.ser.is_open:
            print("Serial port not open")
            return False
            
        # Send begin marker
        if not self._send_and_check(b"Beg\n\r", "OK"):
            print("Failed to establish connection")
            return False
            
        # Send BW data
        print("Sending BW data...")
        if not self._send_data_with_checksum(bw_data):
            print("BW data transmission failed")
            return False
            
        # Send RW data
        print("Sending RW data...")
        if not self._send_data_with_checksum(rw_data):
            print("RW data transmission failed")
            return False
            
        print("Data transmission completed successfully")
        return True
        
    def _send_data_with_checksum(self, data: bytes) -> bool:
        """Send data with checksum verification
        
        Args:
            data: data to send (must be multiple of 16 bytes)
            
        Returns:
            bool: True if all chunks were sent successfully
        """
        total_len = len(data)
        if total_len % 16 != 0:
            print("Data length must be multiple of 16")
            return False
            
        sent = 0
        while sent < total_len:
            chunk = data[sent:sent+16]
            checksum = sum(chunk) & 0xFFFF  # 16-bit checksum
            
            # Send chunk
            if self.ser.write(chunk) != 16:
                print("Failed to send complete chunk")
                return False
                
            # Verify checksum
            expected_response = str(checksum).encode()
            if not self._check_response(expected_response):
                print(f"Checksum verification failed for chunk {sent}-{sent+16}")
                return False
                
            sent += 16
            print(f"Sent {sent}/{total_len} bytes ({sent/total_len*100:.1f}%)", end='\r')
            
        print()  # New line after progress
        return True
        
    def _send_and_check(self, data: bytes, expected: str) -> bool:
        """Send data and verify response
        
        Args:
            data: data to send
            expected: expected response
            
        Returns:
            bool: True if response matches expected
        """
        self.ser.write(data)
        return self._check_response(expected.encode())
        
    def _check_response(self, expected: bytes) -> bool:
        """Check for expected response
        
        Args:
            expected: expected response bytes
            
        Returns:
            bool: True if received expected response
        """
        timeout = time.time() + self.timeout
        while time.time() < timeout:
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting)
                if expected in response:
                    return True
            time.sleep(0.1)
            
        return False

# Example usage
if __name__ == "__main__":
    # Initialize with test data
    test_bw = bytes([i % 256 for i in range(256)])  # 16 chunks of 16 bytes
    test_rw = bytes([255 - (i % 256) for i in range(256)])
    
    # Create and open serial port
    ser = SerialPort("COM3")  # Change to your COM port
    if ser.open():
        try:
            # Send test data
            success = ser.send_img_data(test_bw, test_rw)
            print("Success" if success else "Failed")
        finally:
            ser.close()
