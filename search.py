from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# 載入 Excel 資料
EXCEL_FILE_PATH = './data/package.xlsx'
data = pd.read_excel(EXCEL_FILE_PATH)

# 首頁
@app.route('/')
def index():
    return render_template('index.html')

# 搜尋功能
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    selected_day = int(request.form.get('day', 3))  # 預設為 3 天

    if not query:
        return render_template('result.html', place="未知地點", packages=[], selected_day=selected_day)

    # 從 Excel 中篩選資料
    filtered_data = data[(data['Country'] == query) & (data['Day'] == selected_day)]
    packages = []
    if not filtered_data.empty:
        low_package = filtered_data[filtered_data['Price_level'] == "low"].iloc[0] if 'low' in filtered_data['Price_level'].values else None
        medium_package = filtered_data[filtered_data['Price_level'] == "medium"].iloc[0] if 'medium' in filtered_data['Price_level'].values else None
        high_package = filtered_data[filtered_data['Price_level'] == "high"].iloc[0] if 'high' in filtered_data['Price_level'].values else None

        packages.append({
            "low_id": low_package['Trip_ID'] if low_package is not None else None,
            "medium_id": medium_package['Trip_ID'] if medium_package is not None else None,
            "high_id": high_package['Trip_ID'] if high_package is not None else None
        })

    return render_template('result.html', place=query, packages=packages, selected_day=selected_day)

# 旅遊包詳細頁面
@app.route('/package/<int:trip_id>')
def package_detail(trip_id):
    # 根據 Trip_ID 篩選資料
    package = data[data['Trip_ID'] == trip_id]
    if package.empty:
        return render_template('test2.html', itinerary=[], country="", day=0, tags=[])

    package = package.iloc[0]
    itinerary_details = []
    max_days = int(package['Day'])  # 根據實際天數生成行程
    for day in range(1, max_days + 1):  # 動態處理行程
        attraction_col = f'Attraction_D{day}'
        food_col = f'Food_D{day}'
        stay_col = f'Accommadation_D{day}'

        # 清理並格式化行程、美食和住宿資料
        itinerary_details.append({
            "day": day,
            "places": [place.strip() for place in str(package[attraction_col]).replace("[", "").replace("]", "").replace("'", "").split(",")] if attraction_col in package and not pd.isna(package[attraction_col]) else [],
            "food": [food.strip() for food in str(package[food_col]).replace("[", "").replace("]", "").replace("'", "").split(",")] if food_col in package and not pd.isna(package[food_col]) else [],
            "stay": str(package[stay_col]).replace("[", "").replace("]", "").replace("'", "").strip() if stay_col in package and not pd.isna(package[stay_col]) else ""
        })

    # 處理標籤，移除不必要的符號
    tags = [tag.strip() for tag in package['Tags'].replace("[", "").replace("]", "").replace("'", "").split(",")] if not pd.isna(package['Tags']) else []

    return render_template('package.html', itinerary=itinerary_details, country=package['Country'], day=max_days, tags=tags)

if __name__ == '__main__':
    app.run(debug=True)
