from flask import Flask, render_template, request, jsonify
import yfinance as yf
from datetime import date

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

@app.route('/api/get-stock-data', methods=['POST'])
def get_stock_data():
    stock_codes = request.json.get('stockCodes', [])
    stock_data = {}
    for code in stock_codes:
        ticker = f"{code}.T"
        try:
            stock_info = yf.Ticker(ticker).info
            
            # 日本語名を辞書から取得し、見つからない場合はyfinanceの英語名を取得
            name = STOCK_NAMES_JP.get(code, stock_info.get('longName', '企業名不明'))
            
            # 配当利回り（小数）を取得し、存在しない場合は0.0を返す
            dividend_yield = stock_info.get('dividendYield', 0.0)
            
            # yfinanceは配当利回り（%）をそのまま返す場合があるため、100倍の処理は削除
            # 小数点以下2桁に丸める
            dividend_yield_percent = round(dividend_yield, 2)
            
            stock_data[code] = {
                'name': name,
                'dividendYield': dividend_yield_percent
            }
        except Exception as e:
            # エラー発生時も空のデータで継続
            stock_data[code] = {
                'name': STOCK_NAMES_JP.get(code, '取得失敗'),
                'dividendYield': 'N/A'
            }
    return jsonify(stock_data)

@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    user_thoughts = request.json.get('userThoughts', '')
    stock_data = request.json.get('stockData', {})
    
    # 日付を自動生成
    today_date_str = date.today().strftime("%Y年%m月%d日")
    
    # 投稿文の生成ロジック
    post_text = f"{user_thoughts}\n"
    post_text += f"\n本日の購入({today_date_str})"
    
    for code, data in stock_data.items():
        if data['dividendYield'] != 'N/A':
            post_text += f"\n<{code}> {data['name']} {data['dividendYield']}%"
        else:
            post_text += f"\n<{code}> {data['name']} 情報取得失敗"

    post_text += "\n\n#高配当投資"
    
    return jsonify({
        "postText": post_text,
        "success": True
    })

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
