import numpy as np
from PIL import Image, ImageDraw
import argparse
import os
import cv2

def add_white_background_to_subject(input_path, output_path, padding=10, bg_color=(255, 255, 255, 255), 
                                   edge_color=(240, 240, 240, 255), edge_width=2, smoothness=1):
    """
    Add a white background only to the subject in a PNG image, with a clean border
    
    Args:
        input_path: Path to input PNG image
        output_path: Path to save output image
        padding: Extra padding around the subject in pixels
        bg_color: Background color in RGBA format (default: white)
        edge_color: Edge/border color in RGBA format
        edge_width: Width of the edge in pixels
        smoothness: How smooth to make the edges (higher = smoother)
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
    
    if not contours:
        print("No contours found in the image")
        return False
    
    # Create a mask for the subject area with padding
    subject_mask = np.zeros_like(binary_mask)
    edge_mask = np.zeros_like(binary_mask)
    
    # Draw filled contours for the subject area
    cv2.drawContours(subject_mask, contours, -1, 255, -1)  # -1 means fill
    
    # Apply dilation to add padding around the subject
    if padding > 0:
        kernel = np.ones((padding, padding), np.uint8)
        padded_mask = cv2.dilate(subject_mask, kernel, iterations=1)
    else:
        padded_mask = subject_mask.copy()
    
    # Create edge mask by finding the difference between padded and original
    edge_mask = cv2.subtract(padded_mask, subject_mask)
    
    # Apply smoothing if needed
    if smoothness > 0:
        edge_mask = cv2.GaussianBlur(edge_mask, (smoothness*2+1, smoothness*2+1), 0)
        padded_mask = cv2.GaussianBlur(padded_mask, (smoothness*2+1, smoothness*2+1), 0)
    
    # Create a new transparent image
    result_array = np.array(img.copy())
    
    # Apply white background where the subject and padding is
    for i in range(img.height):
        for j in range(img.width):
            # Apply edge color
            if edge_mask[i, j] > 0:
                # Edge area - apply edge color with alpha from mask
                e_r, e_g, e_b, e_a = edge_color
                edge_alpha = min(edge_mask[i, j], e_a)
                
                # If this is fully transparent in original, use edge color
                if alpha_channel[i, j] == 0:
                    result_array[i, j] = [e_r, e_g, e_b, edge_alpha]
                # Otherwise blend with original
                else:
                    orig_r, orig_g, orig_b, orig_a = img_array[i, j]
                    blend_factor = edge_alpha / 255.0
                    result_array[i, j] = [
                        int(orig_r * (1 - blend_factor) + e_r * blend_factor),
                        int(orig_g * (1 - blend_factor) + e_g * blend_factor),
                        int(orig_b * (1 - blend_factor) + e_b * blend_factor),
                        max(orig_a, edge_alpha)
                    ]
            
            # Apply background color to subject area
            elif subject_mask[i, j] > 0:
                # This is the subject area - apply background color
                bg_r, bg_g, bg_b, bg_a = bg_color
                
                # If pixel has transparency, apply background
                if alpha_channel[i, j] < 255:
                    orig_r, orig_g, orig_b, orig_a = img_array[i, j]
                    blend_factor = 1.0 - (orig_a / 255.0)
                    
                    # Blend original with background
                    result_array[i, j] = [
                        int(orig_r * (1 - blend_factor) + bg_r * blend_factor),
                        int(orig_g * (1 - blend_factor) + bg_g * blend_factor),
                        int(orig_b * (1 - blend_factor) + bg_b * blend_factor),
                        255  # Fully opaque
                    ]
                else:
                    # Keep original fully opaque pixels
                    result_array[i, j][3] = 255  # Ensure fully opaque
    
    # Convert back to PIL Image
    result = Image.fromarray(result_array)
    
    # Save the result
    result.save(output_path)
    return True

def main():
    parser = argparse.ArgumentParser(description='Add white background to subject in PNG image')
    parser.add_argument('input', help='Input PNG image path')
    parser.add_argument('--output', '-o', help='Output image path')
    parser.add_argument('--padding', '-p', type=int, default=0, help='Padding around subject in pixels')
    parser.add_argument('--bg-color', '-b', nargs=4, type=int, default=[255, 255, 255, 255], 
                        help='Background color (R G B A)')
    parser.add_argument('--edge-color', '-e', nargs=4, type=int, default=[240, 240, 240, 255], 
                        help='Edge color (R G B A)')
    parser.add_argument('--edge-width', '-w', type=int, default=2, help='Edge width in pixels')
    parser.add_argument('--smoothness', '-s', type=int, default=1, 
                        help='Edge smoothness (0 for sharp edges, higher for smoother)')
    
    args = parser.parse_args()
    
    if not args.output:
        # Generate output filename if not provided
        filename, ext = os.path.splitext(args.input)
        args.output = f"{filename}_white_bg{ext}"
    
    print(f"Adding white background to {args.input}...")
    if add_white_background_to_subject(
        args.input, args.output, args.padding, 
        tuple(args.bg_color), tuple(args.edge_color), 
        args.edge_width, args.smoothness
    ):
        print(f"White background added successfully! Output saved to {args.output}")
    else:
        print("Failed to add white background")

if __name__ == "__main__":
    main()