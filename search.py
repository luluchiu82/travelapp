from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import ast

app = Flask(__name__)

# 設定資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itinerary.db'  # 修改為你的資料庫路徑
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 資料庫模型
class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    day = db.Column(db.Integer)
    price_level = db.Column(db.String(50))
    tags = db.Column(db.String(100))
    attraction_d1 = db.Column(db.Text, nullable=True)
    food_d1 = db.Column(db.Text, nullable=True)
    accommodation_d1 = db.Column(db.Text, nullable=True)
    attraction_d2 = db.Column(db.Text, nullable=True)
    food_d2 = db.Column(db.Text, nullable=True)
    accommodation_d2 = db.Column(db.Text, nullable=True)
    attraction_d3 = db.Column(db.Text, nullable=True)
    food_d3 = db.Column(db.Text, nullable=True)
    accommodation_d3 = db.Column(db.Text, nullable=True)


# 初始化資料庫
def initialize_database():
    db.create_all()

    # 添加測試資料
    if not Itinerary.query.first():
        test_data = Itinerary(
            country="泰國",
            day=3,
            price_level="中等",
            tags="['美食', '海灘']",
            attraction_d1="['前草', '小港']",
            food_d1="['拉麵', '壽司']",
            accommodation_d1="['APA酒店']",
            attraction_d2="['昭披耶河', '曼谷大皇宮']",
            food_d2="['泰式炒麵']",
            accommodation_d2="['The Siam Hotel']",
            attraction_d3="['ICONSIAM', 'Terminal 21']",
            food_d3="['海鮮大餐']",
            accommodation_d3=None
        )
        db.session.add(test_data)
        db.session.commit()


# 清理資料庫
def clean_database():
    with app.app_context():
        all_data = Itinerary.query.all()

        for item in all_data:
            # 清理每日行程資料
            for day in range(1, item.day + 1):
                # 處理行程 (attraction_dX)
                attr_col = f'attraction_d{day}'
                attr_raw = getattr(item, attr_col, None)
                if attr_raw and attr_raw.startswith('['):
                    cleaned_attr = ", ".join(ast.literal_eval(attr_raw))
                    setattr(item, attr_col, cleaned_attr)

                # 處理美食 (food_dX)
                food_col = f'food_d{day}'
                food_raw = getattr(item, food_col, None)
                if food_raw and food_raw.startswith('['):
                    cleaned_food = ", ".join(ast.literal_eval(food_raw))
                    setattr(item, food_col, cleaned_food)

                # 處理住宿 (accommodation_dX)
                stay_col = f'accommodation_d{day}'
                stay_raw = getattr(item, stay_col, None)
                if stay_raw and stay_raw.startswith('['):
                    cleaned_stay = ", ".join(ast.literal_eval(stay_raw))
                    setattr(item, stay_col, cleaned_stay)

        # 提交變更
        db.session.commit()
        print("資料庫清理完成！")


# 查看清理後的資料
@app.route('/showdata')
def showdata():
    all_data = Itinerary.query.all()
    result = []

    for item in all_data:
        daily_details = []
        for day in range(1, item.day + 1):
            daily_details.append({
                "day": day,
                "places": getattr(item, f'attraction_d{day}', ''),
                "food": getattr(item, f'food_d{day}', ''),
                "stay": getattr(item, f'accommodation_d{day}', '')
            })

        result.append({
            "id": item.id,
            "country": item.country,
            "day": item.day,
            "price_level": item.price_level,
            "tags": item.tags,
            "daily_details": daily_details
        })

    return jsonify({"data": result})


# 編輯行程
@app.route('/edit_package/<int:trip_id>', methods=['GET', 'POST'])
def edit_package(trip_id):
    package = Itinerary.query.filter_by(id=trip_id).first()
    if not package:
        return "行程不存在", 404

    itinerary_details = []
    for day in range(1, package.day + 1):
        itinerary_details.append({
            "day": day,
            "places": getattr(package, f'attraction_d{day}', ''),
            "food": getattr(package, f'food_d{day}', ''),
            "stay": getattr(package, f'accommodation_d{day}', '')
        })

    return render_template('edit_package.html', itinerary=itinerary_details, trip_id=trip_id)


if __name__ == '__main__':
    initialize_database()  # 初始化資料庫
    clean_database()  # 清理資料庫
    app.run(debug=True)
