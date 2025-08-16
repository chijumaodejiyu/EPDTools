import cv2
import sys
import numpy as np
from models.Dithering import Dithering
from models.ImgProcesser import ImgProcesser
from models.serial import SerialPort
import os

# Current version of this script
SCRIPT_VERSION = "2.0"

# Language texts
TEXTS = {
    "en": {
        "welcome": "EPD Tools - Image Processing Pipeline v{}",
        "select_lang": "Select language/选择语言: [1] English [2] 中文",
        "lang_error": "Invalid input, using English",
        "enter_image": "Enter image path (default: test/input.jpg): ",
        "enter_port": "Enter COM port (default: COM3): ",
        "select_dither": "Select dithering method [1] Black & White [2] Red & White [3] Red-Black-White (default: 1): ",
        "dither_error": "Invalid selection, using Black & White",
        "processing": "\nProcessing image...",
        "complete": "\nProcessing complete!"
    },
    "zh": {
        "welcome": "EPD工具 - 图像处理流程 v{}",
        "select_lang": "选择语言/Select language: [1] English [2] 中文",
        "lang_error": "输入无效，默认使用英文",
        "enter_image": "输入图片路径 (默认: test/input.jpg): ",
        "enter_port": "输入COM端口 (默认: COM3): ",
        "select_dither": "选择抖动方式 [1] 黑白 [2] 红白 [3] 红黑白 (默认: 1): ",
        "dither_error": "选择无效，使用黑白抖动",
        "processing": "\n正在处理图片...",
        "complete": "\n处理完成!"
    }
}

def main():
    """EPD Tools Main Processing Pipeline v{}
    
    Usage:
        python main.py
        
    Interactive mode with bilingual support
    """.format(SCRIPT_VERSION)

    # Language selection
    lang = "en"
    try:
        lang_choice = input(TEXTS["en"]["select_lang"] + "\n> ")
        lang = "zh" if lang_choice == "2" else "en"
    except:
        print(TEXTS["en"]["lang_error"])
    
    print(TEXTS[lang]["welcome"].format(SCRIPT_VERSION))
    
    # Interactive input
    image_path = input(TEXTS[lang]["enter_image"]) or os.path.join("test", "input.jpg")
    com_port = input(TEXTS[lang]["enter_port"]) or "COM3"
    
    # Dithering method selection
    # Map user choice to actual method names in Dithering class
    dither_methods = {
        "1": "_black_white_dither",
        "2": "_red_white_dither",
        "3": "_red_black_white_dither"
    }
    dither_method = "_black_white_dither"
    try:
        dither_choice = input(TEXTS[lang]["select_dither"]) or "1"
        dither_method = dither_methods.get(dither_choice, "_black_white_dither")
    except:
        print(TEXTS[lang]["dither_error"])
    
    # Create output directory if not exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Verify image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")
            
    except Exception as e:
        print(f"Error loading image: {e}")
        return
        
    # 2. Process image
    print(TEXTS[lang]["processing"])
    print("\n[1/3] " + ("Applying dithering..." if lang == "en" else "正在应用抖动处理..."))
    try:
        dither = Dithering()
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dithered_img = getattr(dither, dither_method)(gray_img)
        
        # Save dithered image
        output_filename = "dithered_" + os.path.basename(image_path)
        output_path = os.path.join(output_dir, output_filename)
        dither.save_image(dithered_img, output_path)
        print(("Saved dithered image to " if lang == "en" else "已保存抖动处理后的图片到 ") + output_path)
        
    except Exception as e:
        print(("Error during dithering: " if lang == "en" else "抖动处理错误: ") + str(e))
        return

    print("[2/3] " + ("Separating colors..." if lang == "en" else "正在分离颜色..."))
    try:
        processor = ImgProcesser()
        bw_data, rw_data, width, height = processor.modulate_brw(
            dithered_img,
            need_preview=True
        )
    except Exception as e:
        print(f"Error during color separation: {e}")
        return
    
    # 3. Send data if COM port specified
    if com_port:
        print(f"\n[3/3] Sending data to {com_port}...")
        try:
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
        except Exception as e:
            print(f"Error during serial communication: {e}")
    else:
        print("\nNo COM port specified - skipping data transmission")
        
    print(TEXTS[lang]["complete"])

if __name__ == "__main__":
    main()
