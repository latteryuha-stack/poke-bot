import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import cloudscraper

# DiscordのWebHook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1531167042798096477/jN55cGkqlvlrJR3b-dFbw50dvYMSxQf6ejuC3V87slWg6xS3y98WXbV4Qvxra9X9lnd5"

# ★監視したい商品をここに何個でも追加できます！
# 「"商品名": "あみあみの商品URL"」の形でカンマ（,）区切りで並べます。
TARGET_PRODUCTS = {
    "蒼海の七傑": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00031509&_gl=1*lrtm6c*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzM1MzYkajI1JGwwJGgw",  
    "THE BEST vol.2": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00030073&_gl=1*19k6yhz*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzM2NTMkajYwJGwwJGgw",        
    "EGGHEAD CRISIS": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00032011&_gl=1*1czftbk*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzM4OTckajUwJGwwJGgw",
    "王族の血統": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00027410&_gl=1*9x2rli*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQwMzAkajU2JGwwJGgw",
    "ROMANCE DAWN": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00017260&_gl=1*13bfw57*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQxMTgkajYwJGwwJGgw",
    "500年後の未来": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00024381&_gl=1*1ukldvb*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQyMTQkajYwJGwwJGgw",
    "新たなる皇帝": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00026307&_gl=1*1fq1ljd*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQzNzckajYwJGwwJGgw",
    "師弟の絆": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00029509&_gl=1*n0uz9i*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQ0MDEkajM2JGwwJGgw",
    "神速の拳": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00028586&_gl=1*x6peg3*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQ0NDEkajYwJGwwJGgw",
    "THE BEST": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00026035&_gl=1*1gwy23v*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQ0NzkkajIyJGwwJGgw",
    "強大な敵": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00019940&_gl=1*1y0oijv*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQ1NTMkajEzJGwwJGgw",
    "頂上決戦": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00018918&_gl=1*14pdaoi*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzQ3ODkkajU0JGwwJGgw",
    "Anime25th collection": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00028258&_gl=1*1rc0pq4*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzUwMzYkajQ0JGwwJGgw",
    "メモリアルコレクション": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00024087&_gl=1*1a4jkni*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzUwODEkajYwJGwwJGgw",
    "CROSS FORCE": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00032592&_gl=1*ezu7dg*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzUyNDUkajU1JGwwJGgw",
    "BRIGHTNESS OF HOPE": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00033515&_gl=1*1yezfx1*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzUzMTgkajQ1JGwwJGgw",
    "DUAL EVOLUTION": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00032015&_gl=1*yjrrqf*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzUzNzgkajUxJGwwJGgw",
    "覚醒の鼓動": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00023455&_gl=1*138vjbb*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzU0MTkkajEwJGwwJGgw",
    "神龍への願い": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00030374&_gl=1*1h0knk6*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzU1NTAkajQ1JGwwJGgw",
    "誇り高き戦闘民族": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00031256&_gl=1*wo99l0*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzU1ODEkajE0JGwwJGgw",
    "怒りの咆哮": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00026037&_gl=1*14wxp35*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzU2MjUkajYwJGwwJGgw",
    "烈火の闘気": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00025212&_gl=1*29civn*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzU2NTIkajMzJGwwJGgw",
    "限界を超えし者": "https://www.amiami.jp/top/detail/detail?gcode=CARD-00027020&_gl=1*1o96plp*_ga*MjAwNTQ3OTg4NC4xNzg1MjMzNTAx*_ga_DNC11S3TQ3*czE3ODUyMzM1MDEkbzEkZzEkdDE3ODUyMzU3MDUkajQ0JGwwJGgw",
}

scraper = cloudscraper.create_scraper()

def send_discord(product_name, url):
    message = f"🚨【緊急】「{product_name}」の在庫を検知しました！今すぐ購入画面へ！\n{url}"
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    try:
        scraper.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
    except Exception as e:
        print("Discord送信エラー:", e)

# Renderを眠らせないためのWebサーバー設定
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

print("🚀 複数商品の爆速巡回監視を開始します！")

# 無限ループで順番にチェック
while True:
    for name, url in TARGET_PRODUCTS.items():
        try:
            response = scraper.get(url)
            html = response.text
            
            if "注文する" in html or "カートに入れる" in html:
                print(f"【判定結果】{name} ➔ 在庫あり！通知を送ります。")
                send_discord(name, url)
            else:
                print(f"【判定結果】{name} ➔ 売り切れ中")

        except Exception as e:
            print(f"{name} アクセスエラー:", e)

        # あみあみからアクセスブロックされないよう、1商品ごとに5秒間隔をあける
        time.sleep(5)

    print("--- 1周完了。次の巡回へ ---")
    time.sleep(10)  # 1周したら10秒待機
