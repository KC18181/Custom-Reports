import sys
from flask import Flask, request
from pymessenger import Bot

app = Flask("My echo bot")

FB_ACCESS_TOKEN = "EAAVOAI9NH3EBO3ZCXz3IZBHdWML5EnlQYIC34ZBCNZAd50zgt2YZCXu2RBoeDZAyFdhI5Xz3QTCbQE9dceKYYNrGxAqvPCQSbKnrHenFsZA9AOTjQhFqUOVZAExkPNMszTMt3YfJZBHZBqsTFZBpSeqhJvf44eZAO3MmxGg3gT2su7g0AjlRpIEF03RGJeIrilcZBvvZCVpKj1Ll1w7ZAE7IC0oIgZDZD"
bot = Bot(FB_ACCESS_TOKEN)

VERIFICATION_TOKEN = "hello"

# 🛠️ **Step 1: Set Messenger Profile (Get Started, Persistent Menu, Greeting)**
def set_messenger_profile():
    """Send API request to configure Messenger Profile."""
    url = f"https://graph.facebook.com/v12.0/me/messenger_profile?access_token={FB_ACCESS_TOKEN}"
    payload = {
        "get_started": {"payload": "get_started_button"},
        "greeting": [
            {
                "locale": "default",
                "text": "Hello {{user_first_name}}! Welcome to I Tanong mo kay kuya KC chatbot. Tap 'Get Started' to begin."
            }
        ],
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": "View Products",
                        "payload": "VIEW_PRODUCTS"
                    },
                    {
                        "type": "postback",
                        "title": "Contact Support",
                        "payload": "CONTACT_SUPPORT"
                    },
                    {
                        "type": "web_url",
                        "title": "Visit Website",
                        "url": "https://example.com",
                        "webview_height_ratio": "full"
                    }
                ]
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Messenger Profile successfully updated: {response.status_code}, {response.json()}")
    else:
        print(f"Error updating Messenger Profile: {response.status_code}, {response.text}")




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
                    
                    if payload == "get_started_button":
                        welcome_message = "Welcome to our chatbot! I'm here to help you. You can:\n- Type 'Show Brands' to see available brands.\n- Ask me questions about our products."
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
    app.run(debug=True, port=8000, use_reloader=True)
