import cv2
import numpy as np
import random

class Dithering:
    def __init__(self):
        # Note: Colors are in BGR format for OpenCV
        self.palettes = {
            'rw': [(255, 255, 255), (0, 0, 255)],    # White-Red
            'bw': [(255, 255, 255), (0, 0, 0)],      # White-Black
            'rbw': [(255, 255, 255), (0, 0, 0), (0, 0, 255)]  # White-Black-Red
        }

    def process_image(self, image_path, mode='bw'):
        """Process image with specified dithering mode
        
        Args:
            image_path: path to input image
            mode: dithering mode (rw, bw, rbw)
            
        Returns:
            Dithered image as numpy array
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not load image from path")
            
        # Convert to grayscale for dithering
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply dithering based on mode
        if mode == 'rw':
            return self._red_white_dither(gray)
        elif mode == 'bw':
            return self._black_white_dither(gray)
        elif mode == 'rbw':
            return self._red_black_white_dither(gray)
        else:
            raise ValueError("Invalid mode. Use 'rw', 'bw' or 'rbw'")

    def _floyd_steinberg(self, image, palette):
        """Apply Floyd-Steinberg dithering algorithm
        
        Args:
            image: input grayscale image
            palette: list of RGB colors to dither to (in BGR format)
            
        Returns:
            Dithered image as numpy array in BGR format
        """
        # Convert palette to grayscale for comparison
        gray_palette = [int(0.299 * c[2] + 0.587 * c[1] + 0.114 * c[0]) 
                       for c in palette]
        
        # Create output image in BGR format
        height, width = image.shape
        output = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Make a copy to work with
        img = image.copy().astype(np.float32)
        
        for y in range(height):
            for x in range(width):
                old_pixel = img[y, x]
                
                # Find closest color in palette
                closest_idx = np.argmin(np.abs(gray_palette - old_pixel))
                color = palette[closest_idx]
                
                # Set output pixel (already in BGR format)
                output[y, x] = color
                
                # Calculate quantization error
                quant_error = old_pixel - gray_palette[closest_idx]
                
                # Distribute error to neighboring pixels
                if x + 1 < width:
                    img[y, x + 1] += quant_error * 7/16
                if y + 1 < height:
                    img[y + 1, x] += quant_error * 5/16
                    if x - 1 >= 0:
                        img[y + 1, x - 1] += quant_error * 3/16
                    if x + 1 < width:
                        img[y + 1, x + 1] += quant_error * 1/16
                        
        return output

    def _red_white_dither(self, gray):
        """Red-White dithering implementation
        
        Args:
            gray: input grayscale image
            
        Returns:
            Dithered image using red-white palette
        """
        return self._floyd_steinberg(gray, self.palettes['rw'])

    def _black_white_dither(self, gray):
        """Black-White dithering implementation
        
        Args:
            gray: input grayscale image
            
        Returns:
            Dithered image using black-white palette
        """
        return self._floyd_steinberg(gray, self.palettes['bw'])

    def _red_black_white_dither(self, gray):
        """Red-Black-White dithering implementation with enhanced red
        
        Args:
            gray: input grayscale image
            
        Returns:
            Dithered image using red-black-white palette
        """
        # Convert grayscale to BGR
        img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        img_float = img.astype(np.float32) / 255.0
        output = np.zeros_like(img_float)
        height, width, _ = img_float.shape
        
        # 红色优先系数
        red_boost = 1.5
        
        for y in range(height):
            for x in range(width):
                b, g, r = img_float[y, x]  # OpenCV uses BGR
                
                # 计算红色倾向
                red_tendency = r - max(g, b)
                
                # 红色优先处理
                if red_tendency > 0.2:  # 明显红色倾向
                    output[y, x] = [0, 0, 1]  # 红色(BGR格式)
                    error = [b, g, r-1]
                else:
                    # 标准处理流程
                    luminance = 0.299*r + 0.587*g + 0.114*b
                    if luminance < 0.33:
                        output[y, x] = [0, 0, 0]  # 黑色
                        error = [b, g, r]
                    elif luminance > 0.66:
                        output[y, x] = [1, 1, 1]  # 白色
                        error = [b-1, g-1, r-1]
                    else:
                        # 中间色调尝试保留红色信息
                        if r > max(g, b)*1.2:
                            output[y, x] = [0, 0, 1]  # 红色
                            error = [b, g, r-1]
                        else:
                            output[y, x] = [0, 0, 0] if random.random() < 0.5 else [1, 1, 1]
                            error = [b - output[y, x, 0], 
                                     g - output[y, x, 1], 
                                     r - output[y, x, 2]]
                
                # 误差扩散（红色通道增强）
                for dx, dy, weight in [(1,0,7/16), (0,1,5/16), (-1,1,3/16), (1,1,1/16)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        # 红色误差增强扩散
                        img_float[ny, nx, 2] += error[2] * weight * red_boost  # 红色通道
                        img_float[ny, nx, 0] += error[0] * weight  # 蓝色通道
                        img_float[ny, nx, 1] += error[1] * weight  # 绿色通道
        
        return (output * 255).astype(np.uint8)

    def save_image(self, image, output_path):
        """Save processed image to file
        
        Args:
            image: numpy array of image to save
            output_path: path to save image to
        """
        cv2.imwrite(output_path, image)

if __name__ == "__main__":
    """Example usage demonstrating all dithering modes
    
    Example:
        # Process image in black-white mode
        dither = Dithering()
        result = dither.process_image("input.jpg", "bw")
        dither.save_image(result, "output_bw.jpg")
        
        # Process image in red-white mode
        result = dither.process_image("input.jpg", "rw") 
        dither.save_image(result, "output_rw.jpg")
        
        # Process image in red-black-white mode
        result = dither.process_image("input.jpg", "rbw")
        dither.save_image(result, "output_rbw.jpg")
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Image dithering tool')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', help='Output image path')
    parser.add_argument('--mode', choices=['rw', 'bw', 'rbw'], 
                       default='bw', help='Dithering mode')
    
    args = parser.parse_args()
    
    dither = Dithering()
    try:
        result = dither.process_image(args.input, args.mode)
        dither.save_image(result, args.output)
        print(f"Successfully processed image and saved to {args.output}")
    except Exception as e:
        print(f"Error processing image: {str(e)}")
