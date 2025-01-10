from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import ast

app = Flask(__name__)

# 建立資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itinerary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 資料庫樣式
class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    price_level = db.Column(db.String(20), nullable=False)
    tags = db.Column(db.Text, nullable=True)

    # 生成欄位名稱（最多 10 天）
    for i in range(1, 11):  # 假設最多 10 天旅遊包
        locals()[f'attraction_d{i}'] = db.Column(db.Text, nullable=True)
        locals()[f'food_d{i}'] = db.Column(db.Text, nullable=True)
        locals()[f'accommodation_d{i}'] = db.Column(db.Text, nullable=True)

# initialize資料庫並匯入excel資料
def initialize_database():
    with app.app_context():
        db.drop_all()  # 清空
        db.create_all()  # 建立

        # 匯入 Excel 資料
        data = pd.read_excel('./data/package.xlsx')

        for _, row in data.iterrows():
            max_days = int(row['Day'])  # 根據旅遊包類型設定天數
            itinerary = Itinerary(
                id=row['Trip_ID'],
                country=row['Country'],
                day=max_days,
                price_level=row['Price_level'],
                tags=row['Tags'] if 'Tags' in row else None
            )

            # 加入每一天的行程、美食、住宿
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

    # 篩選資料
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

import ast  # 用於轉字串為 Python 結構

@app.route('/package/<int:trip_id>')
def package_detail(trip_id):
    package = Itinerary.query.filter_by(id=trip_id).first()
    if not package:
        return render_template('test2.html', itinerary=[], country="", day=0, tags=[])

    itinerary_details = []
    max_days = package.day  # 幾天的旅遊包
    for day in range(1, max_days + 1):
        # 獲取每一天的旅遊包
        attraction_col = getattr(package, f'attraction_d{day}', None)
        food_col = getattr(package, f'food_d{day}', None)
        accommodation_col = getattr(package, f'accommodation_d{day}', None)

        # 如果是字串形式的 JSON，轉為 Python 列表
        places_list = ast.literal_eval(attraction_col) if attraction_col else []
        food_list = ast.literal_eval(food_col) if food_col else []
        stay = ast.literal_eval(accommodation_col)[0] if accommodation_col else None

        itinerary_details.append({
            "day": day,
            "places": places_list,
            "food": food_list,
            "stay": stay
        })

    # Tag欄位的資料處理
    tags = ast.literal_eval(package.tags) if package.tags else []

    return render_template('package.html', itinerary=itinerary_details, country=package.country, day=max_days, tags=tags, trip_id=trip_id)

@app.route('/edit_package/<int:trip_id>', methods=['GET', 'POST'])
def edit_package(trip_id):
    package = Itinerary.query.filter_by(id=trip_id).first()
    if not package:
        return "行程不存在", 404

    if request.method == 'POST':
        for day in range(1, package.day + 1):
            # 處理行程
            new_places = request.form.getlist(f'places-{day}')  # 獲取行程輸入框的數據
            formatted_places = [p.strip() for p in new_places if p.strip()]  # 去掉空值並去掉多餘空格
            setattr(package, f'attraction_d{day}', str(formatted_places))  # 儲存為 JSON 字串格式

            # 處理美食
            new_foods = request.form.getlist(f'food-{day}')  # 獲取美食輸入框的數據
            formatted_foods = [f.strip() for f in new_foods if f.strip()]  # 去掉空值並去掉多餘空格
            setattr(package, f'food_d{day}', str(formatted_foods))  # 儲存為 JSON 字串格式

            # 處理住宿
            new_stay = request.form.get(f'stay-{day}', '').strip()  # 獲取住宿輸入框的數據
            if new_stay:  # 如果有輸入住宿
                setattr(package, f'accommodation_d{day}', str([new_stay]))  # 包裝成 JSON 字串格式的列表
            else:
                setattr(package, f'accommodation_d{day}', None)  # 如果沒輸入，設為 None

        db.session.commit()
        return redirect(f'/package/{trip_id}')

    # 將數據還原為前端需要的格式
    itinerary_details = []
    for day in range(1, package.day + 1):
        itinerary_details.append({
            "day": day,
            "places": ast.literal_eval(getattr(package, f'attraction_d{day}', '') or '[]'),
            "food": ast.literal_eval(getattr(package, f'food_d{day}', '') or '[]'),
            "stay": ast.literal_eval(getattr(package, f'accommodation_d{day}', '') or '[]')[0] if getattr(package, f'accommodation_d{day}', '') else ""
        })

    return render_template('edit_package.html', itinerary=itinerary_details, trip_id=trip_id)

# 用來檢查資料型態
@app.route('/showdata')
def showdata():
    # 從資料庫中抓取所有行程資料
    all_data = Itinerary.query.all()
    result = []

    for item in all_data:
        # 主要資料
        data = {
            "id": item.id,
            "country": item.country,
            "day": item.day,
            "price_level": item.price_level,
            "tags": item.tags,
        }
        
        # 詳細資料
        daily_details = []
        for day in range(1, item.day + 1):
            daily_details.append({
                "day": day,
                "places": getattr(item, f"attraction_d{day}", None),
                "food": getattr(item, f"food_d{day}", None),
                "stay": getattr(item, f"accommodation_d{day}", None),
            })
        
        data["daily_details"] = daily_details
        result.append(data)
    
    # 返回資料
    return {"data": result}


if __name__ == '__main__':
    initialize_database()  # 初始化
    app.run(debug=True)
