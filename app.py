import os, sys
from flask import Flask, request
from pymessenger import Bot

app = Flask("My echo bot")

FB_ACCESS_TOKEN = "EAAVOAI9NH3EBOzSrrxuvZAScXbRsbXZA8uTKSOdwEmCMGFanL5oOPYTs0kGnp2pZCZC9vBCCHwcZAHsBMUEln0ZABFMKxH2natLeQb7598JjlVHjsVc3ZATKVuWycKQ8aOlQs1X2Pyu9Lgqw9Qyd5GlRXjvSnbqVGGO9MrepLDsHbYhU19O3HS5ISwZCd7OHNmVZByQZDZD"
bot = Bot(FB_ACCESS_TOKEN)

VERIFICATION_TOKEN = "hello"


@app.route('/', methods=['GET'])
def verify():
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == "hello":
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
# 	print(request.data)
	data = request.get_json()
	log(data)

	if data['object'] == "page":
		entries = data['entry']

		for entry in entries:
			messaging = entry['messaging']

			for messaging_event in messaging:

				sender_id = messaging_event['sender']['id']
				recipient_id = messaging_event['recipient']['id']

				if messaging_event.get('message'):
					# HANDLE NORMAL MESSAGES HERE
					if messaging_event['message'].get('text'):
						# HANDLE TEXT MESSAGES
						query = messaging_event['message']['text']
						# ECHO THE RECEIVED MESSAGE
						bot.send_text_message(sender_id, query)
	return "ok", 200

def log(message):
	print(message)
	sys.stdout.flush()


if __name__ == "__main__":
	app.run(debug= True, port=8000, use_reloader = True)