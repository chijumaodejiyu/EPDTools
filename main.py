import cv2
import sys
import numpy as np
from models.Dithering import Dithering
from models.ImgProcesser import ImgProcesser
from models.serial import SerialPort

import os

def main():
    """EPD Tools Main Processing Pipeline
    
    Usage:
        python main.py [image_path] [com_port]
        
    Defaults:
        image_path = /test/input.jpg
        com_port = COM3
    """
    print("EPD Tools - Image Processing Pipeline")
    
    # 1. Set default parameters
    image_path = sys.argv[1] if len(sys.argv) > 1 else "test\input.jpg"
    com_port = sys.argv[2] if len(sys.argv) > 2 else "COM3"
    
    # Create output directory if not exists
    os.makedirs("/output", exist_ok=True)
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image from {image_path}")
            return
    except Exception as e:
        print(f"Error loading image: {e}")
        return
        
    # 2. Process image
    print("\n[1/3] Applying dithering...")
    dither = Dithering()
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dithered_img = dither._black_white_dither(gray_img)
    
    # Save dithered image
    output_path = os.path.join("/output", "dithered_" + os.path.basename(image_path))
    dither.save_image(dithered_img, output_path)
    print(f"Saved dithered image to {output_path}")
    
    print("[2/3] Separating colors...")
    processor = ImgProcesser()
    bw_data, rw_data, width, height = processor.modulate_brw(
        dithered_img,
        need_preview=True,
        lower_red=np.array([0, 50, 50]),
        upper_red=np.array([10, 255, 255]),
        red_th=10,
        black_th=50
    )
    
    # 3. Send data if COM port specified
    if com_port:
        print(f"\n[3/3] Sending data to {com_port}...")
        ser = SerialPort(com_port)
        if ser.open():
            try:
                if ser.send_img_data(bw_data, rw_data):
                    print("Data sent successfully!")
                else:
                    print("Data transmission failed")
            finally:
                ser.close()
        else:
            print("Failed to open serial port")
    else:
        print("\nNo COM port specified - skipping data transmission")
        
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
