import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import cloudscraper

WEBHOOK_URL = "https://discord.com/api/webhooks/1531167042798096477/jN55cGkqlvlrJR3b-dFbw50dvYMSxQf6ejuC3V87slWg6xS3y98WXbV4Qvxra9X9lnd5"
PRODUCT_URL = "https://www.amiami.jp/top/detail/detail?gcode=CARD-00028242"

scraper = cloudscraper.create_scraper()

def send_discord(message):
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    try:
        scraper.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
    except Exception as e:
        print("Discord送信エラー:", e)

# クラウド上で常時動かすための簡易Webサーバー
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

print("🚀 30秒間隔の爆速監視を開始します！")

# 30秒おきの無限ループ
while True:
    try:
        response = scraper.get(PRODUCT_URL)
        html = response.text
        
        if "注文する" in html or "カートに入れる" in html:
            print("【判定結果】在庫あり！")
            send_discord(f"🚨【緊急】あみあみで在庫を検知！今すぐ購入画面へ！\n{PRODUCT_URL}")
        else:
            print("【判定結果】売り切れ中（30秒後に再チェック）")

    except Exception as e:
        print("アクセスエラー:", e)

    time.sleep(30)  # 30秒ごとに実行
