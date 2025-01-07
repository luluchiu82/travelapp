from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)

# 配置資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itinerary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 資料庫模型
class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    price_level = db.Column(db.String(20), nullable=False)
    tags = db.Column(db.Text, nullable=True)

    # 動態生成欄位名稱（最多支援 10 天）
    for i in range(1, 11):  # 假設最多 10 天行程
        locals()[f'attraction_d{i}'] = db.Column(db.Text, nullable=True)
        locals()[f'food_d{i}'] = db.Column(db.Text, nullable=True)
        locals()[f'accommodation_d{i}'] = db.Column(db.Text, nullable=True)

# 初始化資料庫並匯入 Excel 資料
def initialize_database():
    with app.app_context():
        db.drop_all()  # 清空資料表
        db.create_all()  # 建立資料表

        # 匯入 Excel 資料
        excel_path = './data/package.xlsx'  # 確保檔案位於正確位置
        data = pd.read_excel(excel_path)

        for _, row in data.iterrows():
            max_days = int(row['Day'])  # 根據行程天數確定最大天數
            itinerary = Itinerary(
                id=row['Trip_ID'],
                country=row['Country'],
                day=max_days,
                price_level=row['Price_level'],
                tags=row['Tags'] if 'Tags' in row else None
            )

            # 動態加入每一天的行程、美食、住宿
            for day in range(1, max_days + 1):
                attraction_col = f'Attraction_D{day}'
                food_col = f'Food_D{day}'
                accommodation_col = f'Accommadation_D{day}'

                if attraction_col in row and not pd.isna(row[attraction_col]):
                    setattr(itinerary, f'attraction_d{day}', row[attraction_col])
                if food_col in row and not pd.isna(row[food_col]):
                    setattr(itinerary, f'food_d{day}', row[food_col])
                if accommodation_col in row and not pd.isna(row[accommodation_col]):
                    setattr(itinerary, f'accommodation_d{day}', row[accommodation_col])

            db.session.add(itinerary)

        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    selected_day = int(request.form.get('day', 3))  # 預設為 3 天

    if not query:
        return render_template('result.html', place="未知地點", packages=[], selected_day=selected_day)

    # 從資料庫篩選資料
    filtered_data = Itinerary.query.filter_by(country=query, day=selected_day).all()
    packages = []
    if filtered_data:
        low_package = next((item for item in filtered_data if item.price_level == "low"), None)
        medium_package = next((item for item in filtered_data if item.price_level == "medium"), None)
        high_package = next((item for item in filtered_data if item.price_level == "high"), None)

        packages.append({
            "low_id": low_package.id if low_package else None,
            "medium_id": medium_package.id if medium_package else None,
            "high_id": high_package.id if high_package else None
        })

    return render_template('result.html', place=query, packages=packages, selected_day=selected_day)

@app.route('/package/<int:trip_id>')
def package_detail(trip_id):
    # 根據 Trip_ID 查詢資料
    package = Itinerary.query.filter_by(id=trip_id).first()
    if not package:
        return render_template('test2.html', itinerary=[], country="", day=0, tags=[])

    itinerary_details = []
    max_days = package.day  # 獲取行程天數
    for day in range(1, max_days + 1):
        # 動態取出欄位內容
        attraction_col = getattr(package, f'attraction_d{day}', None)
        food_col = getattr(package, f'food_d{day}', None)
        accommodation_col = getattr(package, f'accommodation_d{day}', None)

        itinerary_details.append({
            "day": day,
            "places": eval(attraction_col) if attraction_col else [],  # 轉換為列表
            "food": eval(food_col) if food_col else [],
            "stay": eval(accommodation_col)[0] if accommodation_col and accommodation_col.startswith('[') else accommodation_col
        })

    # 標籤處理
    tags = eval(package.tags) if package.tags else []

    return render_template('package.html', itinerary=itinerary_details, country=package.country, day=max_days, tags=tags)

if __name__ == '__main__':
    initialize_database()  # 初始化資料庫並匯入資料
    app.run(debug=True)
