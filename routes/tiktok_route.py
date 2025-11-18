import http
import logging
import os
from dotenv import load_dotenv
from flask import Flask, request
import requests
from config.logger_conf import setup_logger
from services.tiktok_service import TikTokService
from pyngrok import ngrok, conf

logger = setup_logger()
app = Flask(__name__)
load_dotenv()


ts = TikTokService(os.getenv("CLIENT_ID"),os.getenv("CLIENT_SECRET"))
conf.get_default().auth_token = os.getenv("NGROK_TOKEN")
public_url = ngrok.connect(5000,"http")

HTTPS_REDIRECT_URI = f"{public_url}/callback"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        logger.error("failedto receive tiktok oauthCode !")
    print(code)

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    payload = {
        "client_key": ts.client_id,
        "client_secret": ts.client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": HTTPS_REDIRECT_URI
    }
    res = requests.post(token_url, json=payload)
    print(res)
    return res.json()


    


