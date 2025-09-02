from flask import Flask, request, jsonify, render_template
import yfinance as yf
from datetime import date
import os

app = Flask(__name__)

# ★★★ ここに株式コードと日本語名のマッピング辞書を追加 ★★★
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

# 株式コードから企業名と配当利回り（%）を取得する関数
def get_stock_info(ticker_symbol):
    """
    指定されたティッカーシンボル（株式コード）から企業名と配当利回り（%）を取得します。
    日本の株式の場合、通常末尾に「.T」を付けます。
    
    Args:
        ticker_symbol (str): 株式コード（例: "3388"）。
        
    Returns:
        dict: 企業名と配当利回り%を含む辞書。情報取得に失敗した場合はデフォルト値。
    """
    try:
        # ★★★ 辞書から日本語名を取得。見つからない場合はyfinanceで英語名を取得 ★★★
        name = STOCK_NAMES_JP.get(ticker_symbol, None)
        if not name:
            # Yahoo Financeでの日本の株式は、コードの末尾に ".T" を付けます
            stock = yf.Ticker(f"{ticker_symbol}.T")
            info = stock.info
            name = info.get('longName', '企業名不明')

        # 配当利回りの取得。yfinanceはパーセンテージ値（例: 4.17）で返す場合があるため、
        # そのまま使用します。'dividendYield' がない場合は 0.0 を返します。
        stock = yf.Ticker(f"{ticker_symbol}.T")
        info = stock.info
        dividend_rate = info.get('dividendYield', 0)
        
        return {"name": name, "dividendYield": f"{dividend_rate:.2f}"}
    except Exception as e:
        # エラーが発生した場合、コンソールに詳細を出力
        print(f"エラー: 株式コード {ticker_symbol} の情報を取得できませんでした。エラー詳細: {e}")
        return {"name": "企業名不明", "dividendYield": "0.00"}

# ルートURL ('/') にアクセスがあった際に 'index.html' を表示
@app.route('/')
def index():
    return render_template('index.html')

# 株式コードに基づいて株価データを取得するAPIエンドポイント
@app.route('/api/get-stock-data', methods=['POST'])
def api_get_stock_data():
    data = request.json
    stock_codes = data.get('stockCodes', []) # リクエストボディから株式コードのリストを取得
    
    results = {}
    for code in stock_codes:
        # 各株式コードについて情報を取得し、結果に格納
        results[code] = get_stock_info(code)
    
    # 取得したデータをJSON形式で返す
    return jsonify(results)

# ユーザーの入力と株価データに基づいてX投稿文を生成するAPIエンドポイント
@app.route('/api/generate-post', methods=['POST'])
def api_generate_post():
    data = request.json
    user_thoughts_input = data.get('userThoughts', '') # ユーザーの感想
    # 取得済みの株価データ（辞書形式: {コード: {名前: "", 配当利回り: ""}}）
    fetched_stock_data = data.get('stockData', {}) 
    
    # 今日の日付を YYYY年MM月DD日 形式で自動生成
    today_date_str = date.today().strftime("%Y年%m月%d日")
    
    purchase_details_text = ""
    # 取得済みの株価データを使って投稿文の購入部分を作成
    for code, info in fetched_stock_data.items():
        company_name = info.get('name', '企業名不明')
        dividend_yield_percent = info.get('dividendYield', '0.00')
        purchase_details_text += f"<{code}> {company_name} {dividend_yield_percent}%\n"
    
    # 全体の投稿文を組み立てる
    post_content = f"""
{user_thoughts_input.strip()}

本日の購入({today_date_str})
{purchase_details_text.strip()}
"""
    # 生成された投稿文をJSON形式で返す
    return jsonify({"postText": post_content.strip()})

# スクリプトが直接実行された場合にWebアプリを起動
if __name__ == '__main__':
    # 'templates' ディレクトリが存在しない場合、作成
    if not os.path.exists('templates'):
        os.makedirs('templates')
    # Flaskアプリを実行。debug=Trueで開発中に便利な機能が有効になります。
    app.run(debug=True)
