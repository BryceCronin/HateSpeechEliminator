from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent
import requests
from windows_toasts import Toast, WindowsToaster
toaster = WindowsToaster('Hate Speech Eliminator')

def setup_and_run_comments(openai_api_key, tiktok_username, print_lock):
    # Create the client with optional parameters
    client: TikTokLiveClient = TikTokLiveClient(unique_id=tiktok_username)

    # Listen to the comment event
    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        commenter_username = event.user.nickname  # Get the commenter's username
        comment_text = event.comment
        response = analyze_comment(comment_text, openai_api_key, "context.txt")
        if response and 'choices' in response and response['choices']:
            ai_response = response['choices'][0]['message']['content']
            with print_lock:
                if ai_response == "Negative":
                    print(f"{ai_response} for hate speech. {commenter_username}: \"{comment_text}\"", flush=True)
                elif ai_response == "Positive":
                    print(f"⚠ POTENTIAL HATE SPEECH. {commenter_username}: \"{comment_text}\"", flush=True)
                    alertToast = Toast()
                    alertToast.text_fields = ['⚠ Potential Hate Speech Detected', f'{commenter_username}: "{comment_text}"']
                    toaster.show_toast(alertToast)
        else:
            with print_lock:
                print("No valid response from AI.")

    try:
        # Run the client and block the main thread
        client.run()
    except Exception as e:
        with print_lock:
            print(f"An error occurred: {e}")


def analyze_comment(comment, openai_api_key, context_filename):
    try:
        # Read the content of context.txt
        with open(context_filename, "r") as file:
            context_content = file.read()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Here's a comment from a livestream: {comment}. \n Here's some context about what's happening on the livestream right now:\n{context_content}\n\nBased on the context, let me know if it contains potential hate speech. No need to explain, just say 'Positive' or 'Negative' for hate speech.\n"
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()
    except Exception as e:
        with print_lock:
            print("An error occurred while analysing the image:", e)
        return None
