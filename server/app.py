from flask import Flask
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response, session
from marshmallow import ValidationError
from models import db, bcrypt, User, Note
from schemas import user_schema, note_schema, notes_schema


app = Flask(__name__)

app.config["SECRET_KEY"] = "super-secret-key-change-this-in-production"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)


def make_json_response(data, status_code=200):
    response = make_response(jsonify(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id:
        request.current_user = db.session.get(User, user_id)
    else:
        # No one is logged in
        request.current_user = None


# AUTH ROUTES

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    # Validate the data using marshmallow
    try:
        validated_data = user_schema.load(data)
    except ValidationError as err:
        return make_json_response({"errors": err.messages}, 422)

    existing_user = User.query.filter_by(username=validated_data["username"]).first()
    if existing_user:
        return make_json_response({"error": "Username already taken."}, 422)

    # Create the new user and password is hashed automatically
    new_user = User(username=validated_data["username"])
    new_user.password = validated_data["password"]

    db.session.add(new_user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_json_response({"error": str(e)}, 500)

    # Log the user in by saving their id to the session
    session["user_id"] = new_user.id

    return make_json_response(user_schema.dump(new_user), 201)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return make_json_response({"error": "Username and password are required."}, 400)

    # Find the user by username
    user = User.query.filter_by(username=username).first()

    # Check if user exists and password is correct
    if not user or not user.check_password(password):
        return make_json_response({"error": "Invalid username or password."}, 401)

    # Save user id in the session — keeps them logged in
    session["user_id"] = user.id

    return make_json_response(user_schema.dump(user), 200)


@app.route("/logout", methods=["DELETE"])
def logout():
    session.clear()
    return make_json_response({}, 204)


@app.route("/check_session", methods=["GET"])
def check_session():

    user = request.current_user

    if user:
        return make_json_response(user_schema.dump(user), 200)
    else:
        return make_json_response({"error": "Not logged in."}, 401)


if __name__ == "__main__":
    app.run(port=5555, debug=True)