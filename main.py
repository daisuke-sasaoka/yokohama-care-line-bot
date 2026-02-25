from fastapi import FastAPI, Request, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from dotenv import load_dotenv

WARD_CONTACTS = {
    "青葉区": "青葉区役所 高齢・障害支援課 電話: 045-xxx-xxxx",
    "港北区": "港北区役所 高齢・障害支援課 電話: 045-xxx-xxxx",
    "中区": "中区役所 高齢・障害支援課 電話: 045-xxx-xxxx",
}

load_dotenv()

app = FastAPI()

CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

if CHANNEL_SECRET is None or CHANNEL_ACCESS_TOKEN is None:
    raise ValueError("環境変数が設定されていません")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    body_text = body.decode("utf-8")

    try:
        handler.handle(body_text, signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.lower()
    reply = None  # ← 先に初期化する（重要）

    # 区名チェック
    for ward in WARD_CONTACTS:
        if ward in text:
            reply = f"{ward}の窓口はこちらです。\n{WARD_CONTACTS[ward]}"
            break

    # 区が含まれていなかった場合
    if reply is None:
        if "要介護" in text or "認定" in text:
            reply = "要介護認定の申請はお住まいの区役所の高齢・障害支援課が窓口です。"
        elif "包括" in text or "相談" in text:
            reply = "地域包括支援センターは高齢者の総合相談窓口です。"
        elif "保険料" in text:
            reply = "介護保険料については区役所の保険年金課にお問い合わせください。"
        elif "デイサービス" in text or "在宅" in text:
            reply = "在宅サービスについては地域包括支援センターへ。"
        elif "施設" in text or "老人ホーム" in text:
            reply = "施設入所については区役所または包括支援センターへ。"
        else:
            reply = "どちらの区にお住まいですか？（例：青葉区）"

    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )
