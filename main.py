from flask import Flask, request, abort, render_template
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, PostbackEvent, 
    ButtonsTemplate, PostbackAction, TemplateSendMessage
)

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route('/survey')
def hello():
    name = "who"
    #return name
    return render_template('survey.html', title='アンケート', name=name)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'action':
        buttons_template = ButtonsTemplate(
                title='よくある質問',
                text='質問する内容を選択してください',
                actions=[
                    PostbackAction(label='電源が入っていない',data='button1'),
                    PostbackAction(label='上記以外',data='button2')])
        template_message = TemplateSendMessage(
                alt_text="Buttons alt text",template=buttons_template)
        line_bot_api.reply_message(event.reply_token,template_message)
    elif event.postback.data == 'datetime':
        line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'button1':
        line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='電源を入れてください'))
    elif event.postback.data == 'button2':
        line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='よくある質問をご確認ください。\r\nhttps://www.google.com/'))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
