from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# 讀取 Excel 資料
data = pd.read_excel('./data/package.xlsx')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')  # 從表單獲取搜尋的地點
    if not query:
        query = "未知地點"  # 如果沒有輸入，顯示預設訊息
        return render_template('result.html', place=query)

    # 檢查地點是否在資料中
    if query in data['Country'].values:
        return render_template('result.html', place=query)
    else:
        return render_template('result.html', place=f"抱歉，沒有找到關於 {query} 的結果")

if __name__ == '__main__':
    app.run(debug=True)
