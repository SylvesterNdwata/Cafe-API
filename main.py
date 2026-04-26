from flask import Flask, jsonify, render_template, request, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, func
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns} # type: ignore

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods=["GET"])
def random_cafe():
    cafe = db.session.execute(db.select(Cafe).order_by(func.random()).limit(1)).scalar_one_or_none()
    
    if cafe is None:
        return jsonify({"error": "No cafes found."}), 404
    
    data = {"cafe": cafe.to_dict()} # type: ignore
    return jsonify(data)

@app.route("/all", methods=["GET"])
def all_cafes():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    data = {"cafes": [cafe.to_dict() for cafe in cafes]}
    return jsonify(data)

@app.route("/search", methods=["GET"])
def search_location():
    location = request.args.get("location")
    cafes = db.session.execute(db.select(Cafe).where(Cafe.location.ilike(f"%{location}%"))).scalars().all()
    
    if len(cafes) == 0:
        return jsonify({"cafe": {"Not Found": "Sorry, we dont have a cafe at that location"}})
    
    return jsonify({"cafes": [cafe.to_dict() for cafe in cafes]})


if __name__ == '__main__':
    app.run(debug=True)
