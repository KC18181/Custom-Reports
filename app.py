import sys
from flask import Flask, request
from pymessenger import Bot

app = Flask("My echo bot")

FB_ACCESS_TOKEN = "EAAVOAI9NH3EBOzSrrxuvZAScXbRsbXZA8uTKSOdwEmCMGFanL5oOPYTs0kGnp2pZCZC9vBCCHwcZAHsBMUEln0ZABFMKxH2natLeQb7598JjlVHjsVc3ZATKVuWycKQ8aOlQs1X2Pyu9Lgqw9Qyd5GlRXjvSnbqVGGO9MrepLDsHbYhU19O3HS5ISwZCd7OHNmVZByQZDZD"
bot = Bot(FB_ACCESS_TOKEN)

VERIFICATION_TOKEN = "hello"

# # 🔥 Step 1: Configure the "Get Started" Button
# def set_get_started_button():
#     """Send API request to set the 'Get Started' button."""
#     url = f"https://graph.facebook.com/v12.0/me/messenger_profile?access_token={FB_ACCESS_TOKEN}"
#     payload = {
#         "get_started": {
#             "payload": "{\”type\”:\”legacy_reply_to_message_action\”,\”message\”:\”Get Started\”}"
#         }
#     }
#     response = requests.post(url, json=payload)
#     print(f"Set Get Started Button: {response.status_code}, {response.json()}")


@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFICATION_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)

    if data['object'] == "page":
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']

                # Handle "Get Started" payload
                if messaging_event.get('postback'):
                    payload = messaging_event['postback']['payload']
                    
                    if payload == "GET_STARTED_PAYLOAD":
                        welcome_message = "Welcome to I Tanong mo kay kuya KC chatbot! I'm here to help you. You can:\n- Type 'Show Brands' to see available brands.\n- Ask me questions about our products."
                        bot.send_text_message(sender_id, welcome_message)

                    if payload == "BRAND_APPLE":
                        bot.send_text_message(sender_id, "Here are products for Apple:")
                        bot.send_image_url(sender_id, "https://example.com/images/apple_iphone.jpg")
                        bot.send_text_message(sender_id, "- iPhone 14")
                        bot.send_image_url(sender_id, "https://example.com/images/apple_macbook.jpg")
                        bot.send_text_message(sender_id, "- MacBook Air")
                        bot.send_image_url(sender_id, "https://example.com/images/apple_watch.jpg")
                        bot.send_text_message(sender_id, "- Apple Watch")

                    if payload == "BRAND_SAMSUNG":
                        bot.send_text_message(sender_id, "Here are products for Samsung:")
                        bot.send_image_url(sender_id, "https://example.com/images/samsung_galaxy.jpg")
                        bot.send_text_message(sender_id, "- Galaxy S23")
                        bot.send_image_url(sender_id, "https://example.com/images/samsung_tab.jpg")
                        bot.send_text_message(sender_id, "- Galaxy Tab S8")
                        bot.send_image_url(sender_id, "https://example.com/images/samsung_watch.jpg")
                        bot.send_text_message(sender_id, "- Galaxy Watch 5")

                    if payload == "BRAND_SONY":
                        bot.send_text_message(sender_id, "Here are products for Sony:")
                        bot.send_image_url(sender_id, "https://example.com/images/sony_bravia.jpg")
                        bot.send_text_message(sender_id, "- Sony Bravia TV")
                        bot.send_image_url(sender_id, "https://example.com/images/sony_headphones.jpg")
                        bot.send_text_message(sender_id, "- Sony WH-1000XM5")
                        bot.send_image_url(sender_id, "https://www.bing.com/images/search?view=detailV2&ccid=OcJRg5pD&id=03E263847F47455DCD15538F5CB0CAE8B0C6394A&thid=OIP.OcJRg5pD-4fDETVqIsOpeQHaE7&mediaurl=https%3A%2F%2Fwww.journaldugeek.com%2Fcontent%2Fuploads%2F2022%2F10%2Fps5-sony.jpg&exph=932&expw=1400&q=sony+playstation+5&simid=608053566294472077&FORM=IRPRST&ck=F1D7BB4508F1F571641D0956636613DA&selectedIndex=6&itb=0&cw=1375&ch=751&ajaxhist=0&ajaxserp=0")
                        bot.send_text_message(sender_id, "- Sony PlayStation 5")

                # Handle normal text messages
                if messaging_event.get('message'):
                    if messaging_event['message'].get('text'):
                        query = messaging_event['message']['text'].lower()

                        if query == "show brands":
                            buttons = [
                                {
                                    "type": "postback", 
                                    "title": "Apple", 
                                    "payload": "BRAND_APPLE"
                                },
                                {
                                    "type": "postback", 
                                    "title": "Samsung", 
                                    "payload": "BRAND_SAMSUNG"
                                },
                                {
                                    "type": "postback", 
                                    "title": "Sony", 
                                    "payload": "BRAND_SONY"
                                }
                            ]
                            bot.send_button_message(sender_id, "Select a brand to see products:", buttons)
                        else:
                            bot.send_text_message(sender_id, "Send 'Show Brands' to see available brands.")

    return "ok", 200




def log(message):
    print(message)
    sys.stdout.flush()


if __name__ == "__main__":
    app.run(debug=True, port=1000, use_reloader=True)
