import cv2
import numpy as np

class Dithering:
    def __init__(self):
        self.palettes = {
            'rw': [(255, 255, 255), (255, 0, 0)],    # Red-White
            'bw': [(255, 255, 255), (0, 0, 0)],      # Black-White
            'rbw': [(255, 255, 255), (0, 0, 0), (255, 0, 0)]  # Red-Black-White
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
            palette: list of RGB colors to dither to
            
        Returns:
            Dithered image as numpy array
        """
        # Convert palette to grayscale for comparison
        gray_palette = [int(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) 
                       for c in palette]
        
        # Create output image
        height, width = image.shape
        output = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Make a copy to work with
        img = image.copy().astype(np.float32)
        
        for y in range(height):
            for x in range(width):
                old_pixel = img[y, x]
                
                # Find closest color in palette
                closest_idx = np.argmin(np.abs(gray_palette - old_pixel))
                new_pixel = gray_palette[closest_idx]
                color = palette[closest_idx]
                
                # Set output pixel
                output[y, x] = color
                
                # Calculate quantization error
                quant_error = old_pixel - new_pixel
                
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
        """Red-Black-White dithering implementation
        
        Args:
            gray: input grayscale image
            
        Returns:
            Dithered image using red-black-white palette
        """
        return self._floyd_steinberg(gray, self.palettes['rbw'])

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
