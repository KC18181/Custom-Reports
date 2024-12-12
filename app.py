import sys
from flask import Flask, request
from pymessenger import Bot

app = Flask("My echo bot")

FB_ACCESS_TOKEN = "EAAVOAI9NH3EBOzSrrxuvZAScXbRsbXZA8uTKSOdwEmCMGFanL5oOPYTs0kGnp2pZCZC9vBCCHwcZAHsBMUEln0ZABFMKxH2natLeQb7598JjlVHjsVc3ZATKVuWycKQ8aOlQs1X2Pyu9Lgqw9Qyd5GlRXjvSnbqVGGO9MrepLDsHbYhU19O3HS5ISwZCd7OHNmVZByQZDZD"
bot = Bot(FB_ACCESS_TOKEN)

VERIFICATION_TOKEN = "hello"


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
        entries = data['entry']

        for entry in entries:
            messaging_events = entry['messaging']

            for messaging_event in messaging_events:
                sender_id = messaging_event['sender']['id']

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

                if messaging_event.get('postback'):
                    payload = messaging_event['postback']['payload']

                    if payload == "BRAND_APPLE":
                        bot.send_text_message(sender_id, "Here are products for Apple:\n- iPhone 14\n- MacBook Air\n- Apple Watch")
                    elif payload == "BRAND_SAMSUNG":
                        bot.send_text_message(sender_id, "Here are products for Samsung:\n- Galaxy S23\n- Galaxy Tab S8\n- Galaxy Watch 5")
                    elif payload == "BRAND_SONY":
                        bot.send_text_message(sender_id, "Here are products for Sony:\n- Sony Bravia TV\n- Sony WH-1000XM5\n- Sony PlayStation 5")

    return "ok", 200


def log(message):
    print(message)
    sys.stdout.flush()


if __name__ == "__main__":
    app.run(debug=True, port=8000, use_reloader=True)
