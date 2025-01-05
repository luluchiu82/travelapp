from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itinerary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 資料庫模型
class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    places = db.Column(db.Text, nullable=True)
    food = db.Column(db.Text, nullable=True)
    stay = db.Column(db.Text, nullable=True)

# 初始化資料庫並填入初始數據
def initialize_database():
    with app.app_context():
        db.create_all()
        # 如果資料庫是空的，填入初始行程數據
        if not Itinerary.query.first():
            db.session.add_all([
                Itinerary(day=1, places="秋葉原,原宿", food="XX拉麵店", stay="膳食式旅館"),
                Itinerary(day=2, places="淺草寺,雷門", food="淺草小吃店", stay="膳食式旅館"),
                Itinerary(day=3, places="東京迪士尼樂園", food="", stay="")
            ])
            db.session.commit()

@app.route("/")
def package_page():
    itinerary = Itinerary.query.all()
    return render_template("package.html", itinerary=itinerary)

@app.route("/edit_package", methods=["GET", "POST"])
def edit_package():
    if request.method == "POST":
        itinerary = Itinerary.query.all()
        for item in itinerary:
            places = request.form.getlist(f"places-{item.day}")
            food = request.form.getlist(f"food-{item.day}")
            stay = request.form.get(f"stay-{item.day}")

            item.places = ','.join([p for p in places if p.strip()])
            item.food = ','.join([f for f in food if f.strip()])
            item.stay = stay.strip() if stay and stay.strip() else ""
            db.session.commit()

        return redirect(url_for("package_page"))

    itinerary = Itinerary.query.all()
    return render_template("edit_package.html", itinerary=itinerary)

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
