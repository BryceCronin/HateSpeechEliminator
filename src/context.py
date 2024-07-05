import base64
import requests
from PIL import Image
import io
import logging

def take_screenshot(page):
    while True:
        # Take a screenshot of the element
        #print("New screenshot taken")
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


# Function to encode the image directly from bytes
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')


def analyze_image(image_data, api_key):
    try:
        base64_image = encode_image(image_data)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Explain what's happening (including people, actions, their environment, objects, etc) in this livestream screenshot. Don't provide any formatting. This info will be used for detecting potential hatespeech in the comments, so provide info on race, gender, sex, etc if possible."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print("An error occurred while analyzing image:", e)
        return None


def save_response_to_file(response, filename="context.txt"):
    try:
        message_content = response['choices'][0]['message']['content']
        with open(filename, "w") as file:
            file.write(f"{message_content}\n\n")
    except KeyError as e:
        print(f"KeyError: {e}")
    except Exception as e:
        print(f"An error occurred while saving the response: {e}")
