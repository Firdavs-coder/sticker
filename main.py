from PIL import Image, ImageFilter, ImageChops
from pathlib import Path

class StickerMaker:
    def __init__(
        self,
        alpha_threshold=10,
        border_size=10,
        border_color=(255, 255, 255, 255),
        shadow_size=0,
        shadow_color=(0, 0, 0),
        shadow_transparency=100,
        shadow_blur_strength=6,
        padding=20,
        bg_color=(255, 255, 255, 255),
        bg_transparent=True,
        crop=True
    ):
        """
        Initializes the StickerMaker with parameters for border and shadow. \n
        * `alpha_threshold`: The alpha threshold for transparency detection.
        * `border_size`: The size of the border around the sticker.
        * `border_color`: The color of the border.
        * `shadow_size`: The size of the shadow around the sticker.
        * `shadow_color`: The color of the shadow.
        * `shadow_transparency`: The transparency of the shadow.
        * `shadow_blur_strength`: The strength of the blur applied to the shadow.
        * `padding`: The padding around the cropped image.
        """

        self.alpha_threshold = alpha_threshold
        self.border_size = border_size
        self.border_color = border_color
        self.shadow_size = shadow_size
        self.shadow_color = shadow_color
        self.shadow_transparency = shadow_transparency
        self.shadow_blur_strength = shadow_blur_strength
        self.padding = padding
        self.bg_color = bg_color
        self.bg_transparent = bg_transparent
        self.crop = crop

    def crop_transparent(self, image: Image.Image) -> Image.Image:
        """
        Crops the image to the smallest rectangle that contains all non-transparent pixels,
        and adds padding around it.
        """

        if image.mode != "RGBA":
            raise ValueError("Image must be in RGBA mode for transparency detection.")
        
        bbox = image.getbbox()

        if bbox:
            left, upper, right, lower = bbox
            left = max(0, left - self.padding)
            upper = max(0, upper - self.padding)
            right = min(image.width, right + self.padding)
            lower = min(image.height, lower + self.padding)
            return image.crop((left, upper, right, lower))
        else:
            print("Image is fully transparent.")
            return image

    def make_sticker(self, image_path):
        """
        Creates a sticker from the image at `image_path` by adding a border and shadow.\n
        Returns the final image.
        """

        img = Image.open(image_path).convert("RGBA")

        if self.crop:
            img = self.crop_transparent(img)

        alpha = img.getchannel("A")
        mask = alpha.point(lambda p: 255 if p > self.alpha_threshold else 0)

        dilated = mask.filter(ImageFilter.MaxFilter(self.border_size * 2 + 1))
        border_mask = ImageChops.subtract(dilated, mask)
        border_mask = border_mask.filter(ImageFilter.GaussianBlur(radius=1.5))

       # White border layer
        white_border_layer = Image.new("RGBA", img.size, (255, 255, 255, 255))  # White
        white_border_layer.putalpha(border_mask)

        # Black shadow layer
        shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 255))  # Black
        shadow_mask = border_mask.filter(ImageFilter.GaussianBlur(radius=self.shadow_blur_strength))
        shadow_layer.putalpha(shadow_mask)

        # Combine the layers: First white border, then shadow, then image
        final = Image.alpha_composite(white_border_layer, img)
        final = Image.alpha_composite(shadow_layer, final)

        if not self.bg_transparent:
            black_bg = Image.new("RGBA", img.size, self.bg_color)
            black_bg.paste(final, (0, 0), final)

            return black_bg

        return final
    
    def process(self, input_path, output_path):
        """Processes the image at input_path and saves the final sticker to output_path."""

        final_img = self.make_sticker(input_path)
        final_img.save(output_path, format="PNG")

def process_sticker(image_path: Path):
    """
    Process the uploaded image and convert it to a sticker format
    Args:
        image_path: Path to the uploaded image
    Returns:
        Path to the processed sticker
    """
    with Image.open(image_path) as img:
        # Add your sticker processing logic here
        # For example: resize, add effects, etc.
        processed = img.copy()
        return image_path

# You can add more processing functions here

if __name__ == "__main__":
    sticker = StickerMaker(
            alpha_threshold=100,
            border_size=12,
            border_color=(255, 255, 255, 255),
            shadow_size=0,
            shadow_color=(0, 0, 0),
            shadow_transparency=100,
            shadow_blur_strength=10,
            padding=20,
            bg_color=(187, 189, 191, 255),
            bg_transparent=False,
            crop=False
        ).process(
        input_path="images/image5.png", 
        output_path="outputs/image5.png"
    )
