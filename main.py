from flask import Flask, jsonify, render_template, request
from random import choice
from models.Cafe import Cafe, db

app = Flask(__name__)


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random():
    all_cafes = Cafe.query.all()

    cafe = choice(all_cafes)

    # print(cafe)

    return jsonify(cafe.to_dict())

# HTTP GET - Read Record


@app.route('/all')
def all():
    all_cafes = Cafe.query.all()

    json_cafes = [cafe.to_dict() for cafe in all_cafes]

    return jsonify(json_cafes)


@app.route('/search')
def search():
    args = request.args.to_dict()

    # =func.lower(args['loc'])).all()
    all_cafes = Cafe.query.filter_by(location=args['loc']).all()

    if (len(all_cafes) == 0):
        error = {
            "Not Found": "Sorry, we don't have a cafe at that location"
        }
        return jsonify(error=error)

    json_cafes = [cafe.to_dict() for cafe in all_cafes]

    return jsonify(json_cafes)

# HTTP POST - Create Record


@app.route('/add', methods=['POST'])
def add():
    # print(request.form.to_dict())
    cafe_to_add = request.form.to_dict()

    new_cafe = Cafe(
        name=cafe_to_add['name'],
        map_url=cafe_to_add['map_url'],
        img_url=cafe_to_add['img_url'],
        location=cafe_to_add['location'],
        seats=cafe_to_add['seats'],
        has_toilet=cafe_to_add['has_toilet'] == 'true',
        has_wifi=cafe_to_add['has_wifi'] == 'true',
        has_sockets=cafe_to_add['has_sockets'] == 'true',
        can_take_calls=cafe_to_add['can_take_calls'] == 'true',
        coffee_price=cafe_to_add['coffee_price']
    )
    try:
        db.session.add(new_cafe)
        db.session.commit()
        response = {
            "success": "Successfully added the new cafe"
        }
        return jsonify(response=response), 201
    except Exception as error:
        db.session.rollback()
        print(error)
        response = {
            "error": "Could not add the new cafe"
        }

        return jsonify(response=response), 409


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<id>', methods=['PATCH'])
def update(id: int):
    updated_price = request.form.to_dict()['price']

    try:
        int_id = int(id)
        float_updated_price = float(updated_price)

        cafe_to_update = Cafe.query.filter_by(id=id).first()

        if cafe_to_update == None:
            response = {
                "Not Found": "Sorry a cafe with that id was not found in the database."
            }
            return jsonify(error=response), 404

        cafe_to_update.coffee_price = float_updated_price

        db.session.commit()

        response = {
            "success": "Successfully updated the price."
        }

        return jsonify(response), 200
    except ValueError as error:
        db.session.rollback()
        print(error)
        # error_value = f"{error}"
        response = {
            # "Error": "The id must be an integer value",
            "Description": f"{error}"
        }
        return jsonify(error=response), 406


# HTTP DELETE - Delete Record
if __name__ == '__main__':
    app.run(debug=True, port=5050)
