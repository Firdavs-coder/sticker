from PIL import Image

def add_subject_and_background_colors(image_path, subject_color=(255, 0, 0), background_color=(255, 255, 0)):
    """
    Adds a red background color to the subject and a yellow background color to the remaining transparent background.
    """
    img = Image.open(image_path).convert("RGBA")
    
    # Get the alpha channel (transparency) of the image
    alpha = img.getchannel("A")
    
    # Create a background layer with the yellow color
    background_layer = Image.new("RGBA", img.size, background_color + (255,))

    # Create the subject layer by using the image with its alpha channel for transparency
    subject_layer = Image.new("RGBA", img.size, subject_color + (255,))
    
    # Paste the image onto the subject layer where the alpha is non-zero (subject area)
    subject_layer.paste(img, (0, 0), img)
    
    # Combine the subject layer (with the red background) and the background layer (with the yellow background)
    final = Image.alpha_composite(background_layer, subject_layer)

    
    final.save("output.png", format="PNG")


add_subject_and_background_colors("images/image4.png", subject_color=(0, 0, 0), background_color=(255, 255, 255))