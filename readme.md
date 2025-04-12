# Python Sticker Maker

Python Sticker Maker is a tool for creating custom stickers from images with options for borders, shadows, and background customization.

## Sample Usage
```python
sticker = StickerMaker(
        alpha_threshold=10,
        border_size=16,
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
    input_path="images/image3.png", 
    output_path="outputs/image3.png"
)
```

## Image Comparison Table

| Original Image       | Output Image         |
|-----------------------|----------------------|
| ![Original](images/image1.png) | ![Output](outputs/image1.png) |
| ![Original](images/image2.png) | ![Output](outputs/image2.png) |
| ![Original](images/image3.png) | ![Output](outputs/image3.png) |
| ![Original](images/image4.png) | ![Output](outputs/image4.png) |
