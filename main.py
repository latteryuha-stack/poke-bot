import json
import cloudscraper

WEBHOOK_URL = "https://discord.com/api/webhooks/1531167042798096477/jN55cGkqlvlrJR3b-dFbw50dvYMSxQf6ejuC3V87slWg6xS3y98WXbV4Qvxra9X9lnd5"
PRODUCT_URL = "https://www.amiami.jp/top/detail/detail?gcode=CARD-00028242"

def send_discord(message):
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    scraper.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)

scraper = cloudscraper.create_scraper()

try:
    response = scraper.get(PRODUCT_URL)
    html = response.text
    
    # 在庫がある時だけDiscordへ緊急通知！
    if "注文する" in html or "カートに入れる" in html:
        print("【判定結果】在庫あり！")
        send_discord(f"🚨【緊急】在庫を検知しました！今すぐ購入画面へ！\n{PRODUCT_URL}")
    else:
        print("【判定結果】現在は売り切れ中です。")

except Exception as e:
    print("アクセスエラー:", e)
