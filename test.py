import numpy as np
from PIL import Image, ImageDraw
import argparse
import os
import cv2

def create_clean_border(input_path, output_path, border_width=20, border_color=(220, 220, 220, 255), smoothness=2):
    """
    Add a clean, smooth border to a PNG image with transparency
    
    Args:
        input_path: Path to input PNG image
        output_path: Path to save output image
        border_width: Width of the border in pixels
        border_color: Border color in RGBA format
        smoothness: How smooth to make the border curve (higher = smoother)
    """
    # Open the image
    try:
        img = Image.open(input_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening image: {e}")
        return False
    
    # Convert to numpy array for OpenCV processing
    img_array = np.array(img)
    
    # Extract alpha channel
    alpha_channel = img_array[:,:,3]
    
    # Create binary mask from alpha channel
    _, binary_mask = cv2.threshold(alpha_channel, 1, 255, cv2.THRESH_BINARY)
    
    # Find contours in the binary mask
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a mask image for the border
    border_mask = np.zeros_like(binary_mask)
    
    # Draw the contours with the specified thickness
    cv2.drawContours(border_mask, contours, -1, 255, border_width)
    
    # Create the final border image
    if smoothness > 0:
        # Apply slight Gaussian blur for smoothness
        border_mask = cv2.GaussianBlur(border_mask, (smoothness*2+1, smoothness*2+1), 0)
    
    # Create a new transparent image for the border
    border_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
    
    # Create a mask from the border
    border_mask_pil = Image.fromarray(border_mask)
    
    # Create a drawing context
    draw = ImageDraw.Draw(border_img)
    
    # Apply the color to the border mask
    r, g, b, a = border_color
    
    # Convert to RGBA array
    border_array = np.array(border_img)
    
    # Apply border color where the mask is non-zero
    for i in range(img.height):
        for j in range(img.width):
            if border_mask[i, j] > 0:
                # Only apply border where the original image is transparent
                if alpha_channel[i, j] == 0:
                    # Apply color with alpha from the mask
                    alpha_value = min(border_mask[i, j], a)
                    border_array[i, j] = [r, g, b, alpha_value]
    
    # Convert back to PIL Image
    border_img = Image.fromarray(border_array)
    
    # Create the final image by compositing
    result = Image.new('RGBA', img.size, (0, 0, 0, 0))
    result = Image.alpha_composite(result, border_img)
    result = Image.alpha_composite(result, img)
    
    # Save the result
    result.save(output_path)
    return True

def main():
    parser = argparse.ArgumentParser(description='Add a clean border to a PNG image')
    parser.add_argument('input', help='Input PNG image path')
    parser.add_argument('--output', '-o', help='Output image path')
    parser.add_argument('--width', '-w', type=int, default=20, help='Border width in pixels')
    parser.add_argument('--color', '-c', nargs=4, type=int, default=[220, 220, 220, 255], 
                        help='Border color (R G B A)')
    parser.add_argument('--smoothness', '-s', type=int, default=2, 
                        help='Border smoothness (0 for sharp edges, higher for smoother)')
    
    args = parser.parse_args()
    
    if not args.output:
        # Generate output filename if not provided
        filename, ext = os.path.splitext(args.input)
        args.output = f"{filename}_bordered{ext}"
    
    print(f"Adding border to {args.input}...")
    if create_clean_border(args.input, args.output, args.width, tuple(args.color), args.smoothness):
        print(f"Border added successfully! Output saved to {args.output}")
    else:
        print("Failed to add border")

if __name__ == "__main__":
    main()