from PIL import Image
import io

def take_screenshot(page):
    while True:

        # Take a screenshot of the element
        print("New screenshot taken")
        screenshot_bytes = page.screenshot()

        image = Image.open(io.BytesIO(screenshot_bytes))

        # Get the dimensions of the image
        width, height = image.size

        # Calculate the cropped area (50 pixels from each side)
        left = 114
        top = 122
        right = width - 45
        bottom = height - 160

        cropped_image = image.crop((left, top, right, bottom))

        cropped_image.save("screenshot.png")

        # Save cropped image to bytes
        img_byte_arr = io.BytesIO()
        cropped_image.save(img_byte_arr, format='PNG')
        cropped_image_bytes = img_byte_arr.getvalue()

        return cropped_image_bytes