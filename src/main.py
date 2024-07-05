from playwright.sync_api import sync_playwright
from context import take_screenshot, analyze_image, save_response_to_file
import comments
import time
import threading
from gooey import Gooey, GooeyParser
import sys
from windows_toasts import InteractableWindowsToaster, Toast

interactableToaster = InteractableWindowsToaster('Hate Speech Eliminator')
newToast = Toast()

# Create a lock object
print_lock = threading.Lock()

@Gooey(program_name='Hate Speech Eliminator for TikTok Live', tabbed_groups=True, richtext_controls=True,
       image_dir='icons', default_size=(500, 600), header_bg_color='#E1F5FE', header_height=100,
       header_show_subtitle=False, show_stop_warning=False)
def gooey_main():
    parser = GooeyParser(description="Analyse comments for hate speech using AI context analysis")

    group1 = parser.add_argument_group('Settings')
    group1.add_argument('tiktok_username', metavar="TikTok Username", help="Users must be live. Include the @ symbol.",
                        type=str, default="")

    group2 = parser.add_argument_group('Advanced')
    group2.add_argument('openai_api_key', metavar="OpenAI API Key",
                        help="Create a key at https://platform.openai.com/api-keys",
                        default="", type=str,
                        widget="PasswordField")
    group2.add_argument('interval', metavar="Livestream Analysis Interval",
                        help="Increasing the time between livestream context analysis reduces the required AI processing fees, but also reduces the accuracy of hate speech detection.",
                        type=int, default=30)

    args = parser.parse_args()

    with print_lock:
        print(f"{args.tiktok_username}'s TikTok Livestream is now being monitored for potential hate speech.", flush=True)
        print(f"Context analysis will occur every {args.interval} seconds", flush=True)

    do_stuff(args.openai_api_key, args.tiktok_username, args.interval)


def do_stuff(openai_api_key, tiktok_username, interval):
    screenshot_thread = threading.Thread(target=run_screenshot_analysis,
                                         args=(openai_api_key, tiktok_username, interval))
    comment_thread = threading.Thread(target=comments.setup_and_run_comments, args=(openai_api_key, tiktok_username, print_lock))

    screenshot_thread.start()
    comment_thread.start()

    screenshot_thread.join()
    comment_thread.join()


def run_screenshot_analysis(openai_api_key, tiktok_username, interval):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(0)
        page.set_viewport_size({"width": 720, "height": 1280})
        with print_lock:
            print(f"Navigating to the live page: {tiktok_username}", flush=True)
        page.goto(f"https://www.tiktok.com/{tiktok_username}/live")


        newToast.text_fields = ['Hate Speech Eliminator is now running', 'You may now minimise the app, a notification will alert you if action is needed']
        interactableToaster.show_toast(newToast)

        # Initial delay to ensure the page is fully loaded
        initial_delay = 3  # Adjust the delay time as needed
        with print_lock:
            print(f"Waiting for TikTok Live to load...", flush=True)
            sys.stdout.write("\033[F")
        time.sleep(initial_delay)

        try:
            while True:
                with print_lock:
                    print("Attempting to take a screenshot...", flush=True)
                screenshot = take_screenshot(page)
                if screenshot:
                    with print_lock:
                        print("Screenshot taken, analyzing...", flush=True)
                    response = analyze_image(screenshot, openai_api_key)
                    ai_response = response['choices'][0]['message']['content']
                    with print_lock:
                        print("\nContext updated: ", ai_response, flush=True)
                    save_response_to_file(response)
                else:
                    with print_lock:
                        print("Failed to take screenshot.", flush=True)
                time.sleep(interval)
        except KeyboardInterrupt:
            with print_lock:
                print("Stopped by user.", flush=True)
        except Exception as e:
            with print_lock:
                print(f"An error occurred: {e}", flush=True)
        finally:
            browser.close()


def run_comment_analysis(openai_api_key, tiktok_username):
    try:
        comments.client.run()
    except Exception as e:
        with print_lock:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    gooey_main()
