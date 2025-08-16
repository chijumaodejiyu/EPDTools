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
            "enter_resolution": "Enter target resolution WxH (default: 250x122): ",
        "select_dither": "Select dithering method [1] Black & White [2] Red & White [3] Red-Black-White (default: 1): ",
        "dither_error": "Invalid selection, using Black & White",
        "dither_strength": "Enter dithering strength [1-10] (default: 5): ",
        "dither_strength_error": "Invalid strength, using default 5",
        "rotate_prompt": "Rotate image? [1] No [2] 90° [3] 180° [4] 270° (default: 1): ",
        "rotate_error": "Invalid selection, no rotation applied",
        "preview_prompt": "Preview generated. Are you satisfied? [1] Yes [2] No (default: 1): ",
        "preview_error": "Invalid input, assuming Yes",
            "processing": "\nProcessing image...",
            "complete": "\nProcessing complete!"
        },
    "zh": {
        "welcome": "EPD工具 - 图像处理流程 v{}",
        "select_lang": "选择语言/Select language: [1] English [2] 中文",
        "lang_error": "输入无效，默认使用英文",
        "enter_image": "输入图片路径 (默认: test/input.jpg): ",
        "enter_port": "输入COM端口 (默认: COM3): ",
        "enter_resolution": "输入目标分辨率 WxH (默认: 250x122): ",
        "select_dither": "选择抖动方式 [1] 黑白 [2] 红白 [3] 红黑白 (默认: 1): ",
        "dither_error": "选择无效，使用黑白抖动",
        "dither_strength": "输入抖动强度 [1-10] (默认: 5): ",
        "dither_strength_error": "输入无效，使用默认值5",
        "rotate_prompt": "旋转图片? [1] 否 [2] 90° [3] 180° [4] 270° (默认: 1): ",
        "rotate_error": "选择无效，不旋转图片",
        "preview_prompt": "预览已生成。是否满意? [1] 是 [2] 否 (默认: 1): ",
        "preview_error": "输入无效，默认为是",
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

    # Language selection with validation
    lang = "en"  # default language
    try:
        lang_choice = input(TEXTS["en"]["select_lang"] + "\n> ")
        lang = "zh" if lang_choice == "2" else "en"
        # Ensure lang is valid (either "en" or "zh")
        if lang not in TEXTS:
            lang = "en"
            print(TEXTS["en"]["lang_error"])
    except:
        lang = "en"
        print(TEXTS["en"]["lang_error"])
    
    print(TEXTS[lang]["welcome"].format(SCRIPT_VERSION))
    
    # Interactive input
    image_path = input(TEXTS[lang]["enter_image"]) or os.path.join("test", "input.jpg")
    com_port = input(TEXTS[lang]["enter_port"]) or "COM3"
    
    # Resolution input
    resolution = input(TEXTS[lang]["enter_resolution"]) or "250x122"
    try:
        width, height = map(int, resolution.split('x'))
    except:
        width, height = 250, 122
        print(("Invalid resolution format, using default 250x122" if lang == "en" 
              else "分辨率格式无效，使用默认值250x122"))
    
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

        # Ask if user wants to rotate image
        try:
            rotate_choice = input(TEXTS[lang]["rotate_prompt"]) or "1"
            if rotate_choice == "2":
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif rotate_choice == "3":
                img = cv2.rotate(img, cv2.ROTATE_180)
            elif rotate_choice == "4":
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        except:
            print(TEXTS[lang]["rotate_error"])
            
        # Resize image to target resolution
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
            
    except Exception as e:
        print(f"Error loading image: {e}")
        return
        
    # 2. Process image
    print(TEXTS[lang]["processing"])
    # Dithering strength input
    dither_strength = 5
    try:
        strength_input = input(TEXTS[lang]["dither_strength"]) or "5"
        dither_strength = max(1, min(10, int(strength_input)))
    except:
        print(TEXTS[lang]["dither_strength_error"])
    
    # Processing loop
    satisfied = False
    while not satisfied:
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
            
            # Show preview
            cv2.imshow(("Preview" if lang == "en" else "预览"), dithered_img)
            cv2.waitKey(1000)  # Show for 1 second
            cv2.destroyAllWindows()
            
            # Ask if satisfied
            try:
                satisfied_choice = input(TEXTS[lang]["preview_prompt"]) or "1"
                satisfied = satisfied_choice == "1"
                
                if not satisfied:
                    # Re-ask for parameters
                    dither_choice = input(TEXTS[lang]["select_dither"]) or dither_choice
                    dither_method = dither_methods.get(dither_choice, dither_method)
                    
                    strength_input = input(TEXTS[lang]["dither_strength"]) or str(dither_strength)
                    dither_strength = max(1, min(10, int(strength_input)))
            except Exception as e:
                print(TEXTS[lang]["preview_error"])
                satisfied = True
        
        except Exception as e:
            print(("Error during dithering: " if lang == "en" else "抖动处理错误: ") + str(e))
            return

    print("[2/3] " + ("Separating colors..." if lang == "en" else "正在分离颜色..."))
    try:
        processor = ImgProcesser()
        # Map dither method to mode string
        mode_map = {
            "_black_white_dither": "bw",
            "_red_white_dither": "rw", 
            "_red_black_white_dither": "rbw"
        }
        bw_data, rw_data, width, height = processor.modulate_brw(
            dithered_img,
            need_preview=True,
            dither_mode=mode_map[dither_method]
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
