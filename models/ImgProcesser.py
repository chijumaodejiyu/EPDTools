import cv2
import numpy as np

class ImgProcesser:
    def __init__(self):
        pass

    def modulate_brw(self, img, need_preview=False):
        """Process dithered image for EPD display
        
        Args:
            img: dithered BGR image (only contains specific colors)
            need_preview: whether to show preview
            
        Returns:
            tuple: (bw_data, rw_data, width, height)
        """
        # Auto-rotate if portrait orientation
        if img.shape[1] < img.shape[0]:  # width < height
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            
        # Crop to maintain aspect ratio
        h, w = img.shape[:2]
        target_ratio = w / h
        current_ratio = img.shape[1] / img.shape[0]
        
        if abs(current_ratio - target_ratio) > 0.01:  # Only crop if ratio differs significantly
            if current_ratio > target_ratio:  # Too wide
                new_width = int(h * target_ratio)
                x = (w - new_width) // 2
                img = img[:, x:x+new_width]
            else:  # Too tall
                new_height = int(w / target_ratio)
                y = (h - new_height) // 2
                img = img[y:y+new_height, :]
                
        # Ensure height is multiple of 8
        if img.shape[0] % 8 != 0:
            pad = 8 - (img.shape[0] % 8)
            img = cv2.copyMakeBorder(img, 0, pad, 0, 0, cv2.BORDER_CONSTANT, value=(0,0,0))
            
        height, width = img.shape[:2]
        
        # Create masks for each color
        white_mask = cv2.inRange(img, np.array([255,255,255]), np.array([255,255,255]))
        black_mask = cv2.inRange(img, np.array([0,0,0]), np.array([0,0,0]))
        red_mask = cv2.inRange(img, np.array([0,0,255]), np.array([0,0,255]))
        
        # Create black-white binary (white=1, black=0)
        bw_bin = white_mask
        
        # Create red-white binary (white=1, red=0)
        rw_bin = cv2.bitwise_or(white_mask, red_mask)
        rw_bin = cv2.bitwise_not(rw_bin)
        
        # Preview if needed
        if need_preview:
            preview = bw_bin.copy()
            preview = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR)
            preview[rw_bin == 255] = (0, 0, 255)  # Mark red as blue in preview
            cv2.imshow('Preview', preview)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        # Pack 8 pixels into 1 byte
        bw_data = self._pack_bits(bw_bin)
        rw_data = self._pack_bits(rw_bin)
        
        return bw_data, rw_data, width, height
        
    def _pack_bits(self, binary_img):
        """Pack 8 binary pixels into 1 byte
        
        Args:
            binary_img: binary image (0 or 255)
            
        Returns:
            bytearray: packed data
        """
        height, width = binary_img.shape
        packed = bytearray()
        
        for x in range(width):
            for y in range(0, height, 8):
                byte = 0
                for i in range(8):
                    if y + i < height:
                        # Set bit if pixel is white (255)
                        if binary_img[y + i, x] == 255:
                            byte |= 1 << (7 - i)
                packed.append(byte)
                
        return packed

if __name__ == "__main__":
    # Example usage
    processor = ImgProcesser()
    img = cv2.imread("input.jpg")
    if img is not None:
        bw, rw, w, h = processor.modulate_brw(img, need_preview=True)
        print(f"Generated data - Width: {w}, Height: {h}")
        print(f"BW data length: {len(bw)} bytes")
        print(f"RW data length: {len(rw)} bytes")
    else:
        print("Failed to load image")
