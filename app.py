from flask import Flask, render_template, request, jsonify
import yfinance as yf
import requests

app = Flask(__name__)

# ★★★ 株式コードと日本語名のマッピング辞書 ★★★
STOCK_NAMES_JP = {
    "1605": "INPEX",
    "1802": "大林組",
    "1928": "積水ハウス",
    "2337": "いちご",
    "2503": "キリンHD",
    "2897": "日清食品HD",
    "2914": "JT",
    "3002": "グンゼ",
    "3252": "地主",
    "3388": "明治電機工業",
    "4063": "信越化学工業",
    "4204": "積水化学",
    "4452": "花王",
    "4502": "武田薬品工業",
    "4503": "アステラス製薬",
    "4665": "ダスキン",
    "4996": "クミアイ化学工業",
    "5020": "ENEOS",
    "5108": "ブリジストン",
    "5411": "JFEﾎｰﾙﾃﾞｨﾝｸﾞｽ",
    "6178": "日本郵政",
    "6301": "コマツ",
    "6326": "クボタ",
    "6472": "NTN",
    "7203": "トヨタ",
    "7453": "良品計画",
    "7974": "任天堂",
    "8001": "伊藤忠商事",
    "8031": "三井物産",
    "8058": "三菱商事",
    "8098": "稲畑産業",
    "8173": "上新電機",
    "8267": "イオン",
    "8306": "三菱UFJ",
    "8308": "りそな",
    "8316": "三井住友FG",
    "8473": "SBI HD",
    "8511": "日本証券金融",
    "8591": "オリックス",
    "8593": "三菱HCキャピタル",
    "8697": "日本取引所G",
    "8766": "東京海上HD",
    "8801": "三井不動産",
    "8898": "センチュリー21",
    "9142": "JR九州",
    "9432": "NTT",
    "9433": "KDDI",
    "9434": "ソフトバンク",
    "9513": "Jパワー"
}
# -------------------------------------------------------------

# 株式コードに基づいて株価データを取得するAPIエンドポイント
@app.route('/api/get-stock-data', methods=['POST'])
def get_stock_data():
    stock_codes = request.json.get('stockCodes', [])
    stock_data = {}
    for code in stock_codes:
        ticker = f"{code}.T"
        try:
            stock_info = yf.Ticker(ticker).info
            current_price = stock_info.get('currentPrice', 'N/A')
            open_price = stock_info.get('open', 'N/A')

            # 日本語名を辞書から取得し、見つからない場合はyfinanceの英語名を取得
            name = STOCK_NAMES_JP.get(code, stock_info.get('longName', '企業名不明'))

            if current_price != 'N/A' and open_price != 'N/A':
                change = current_price - open_price
                change_percent = (change / open_price) * 100
                stock_data[code] = {
                    'name': name,
                    'current_price': current_price,
                    'change_price': round(change, 2),
                    'change_percent': round(change_percent, 2)
                }
            else:
                stock_data[code] = {
                    'name': name,
                    'current_price': 'N/A',
                    'change_price': 'N/A',
                    'change_percent': 'N/A'
                }
        except Exception as e:
            # エラー発生時も空のデータで継続
            stock_data[code] = {
                'name': STOCK_NAMES_JP.get(code, '取得失敗'),
                'current_price': 'N/A',
                'change_price': 'N/A',
                'change_percent': 'N/A'
            }
    return jsonify(stock_data)

# ユーザーの入力と株価データに基づいてX投稿文を生成するAPIエンドポイント
@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    user_thoughts = request.json.get('userThoughts', '')
    stock_data = request.json.get('stockData', {})
    
    # 投稿文の生成ロジック
    post_text = f"{user_thoughts}\n"
    for code, data in stock_data.items():
        if data['change_percent'] != 'N/A':
            change_direction = '上昇' if data['change_percent'] > 0 else '下落'
            post_text += f"\n📊{data['name']} ({code}): {data['change_percent']}% {change_direction} ({data['change_price']}円)"
        else:
            post_text += f"\n📊{data['name']} ({code}): 株価情報取得失敗"

    post_text += "\n\n#投資 #株式投資 #日経平均"
    
    # 成功時のレスポンスを正しく返す
    return jsonify({
        "postText": post_text,
        "success": True
    })

# ルートURL ('/') にアクセスがあった際に 'index.html' を表示
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
