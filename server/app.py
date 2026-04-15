from flask import Flask, request, jsonify, make_response, session
from flask_migrate import Migrate
from marshmallow import ValidationError
from models import db, bcrypt, User, Note
from schemas import user_schema, note_schema, notes_schema


app = Flask(__name__)

app.config["SECRET_KEY"] = "super-secret-key-change-this-in-production"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)
bcrypt.init_app(app)



def make_json_response(data, status_code=200):
    response = make_response(jsonify(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response


# BEFORE EVERY REQUEST
# Checks if the user is logged in
@app.before_request
def load_logged_in_user():

    user_id = session.get("user_id")

    if user_id:
        # Try to find the user in the database
        request.current_user = db.session.get(User, user_id)
    else:
        # No one is logged in
        request.current_user = None

# AUTH ROUTES

@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    # Validate the incoming data using marshmallow
    try:
        validated_data = user_schema.load(data)
    except ValidationError as err:
        return make_json_response({"errors": err.messages}, 422)

    # Check if the username is already taken
    existing_user = User.query.filter_by(username=validated_data["username"]).first()
    if existing_user:
        return make_json_response({"error": "Username already taken."}, 422)

    # Create the new user 
    new_user = User(username=validated_data["username"])
    new_user.password = validated_data["password"]  # triggers bcrypt hashing

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

    # search  the user by username
    user = User.query.filter_by(username=username).first()

    # Check if user exists AND password is correct
    if not user or not user.check_password(password):
        return make_json_response({"error": "Invalid username or password."}, 401)

    # Save user id in the session to keep them logged in
    session["user_id"] = user.id

    return make_json_response(user_schema.dump(user), 200)


@app.route("/logout", methods=["DELETE"])
def logout():

    session.clear()  # removes all session data including user_id
    return make_json_response({}, 204)


@app.route("/check_session", methods=["GET"])
def check_session():

    user = request.current_user

    if user:
        return make_json_response(user_schema.dump(user), 200)
    else:
        return make_json_response({"error": "Not logged in."}, 401)

# NOTES ROUTES 

@app.route("/notes", methods=["GET"])
def get_notes():
 
    # Block access if not logged in
    if not request.current_user:
        return make_json_response({"error": "You must be logged in."}, 401)

    # set default page 1, 5 notes per page
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    paginated = (
        Note.query
        .filter_by(user_id=request.current_user.id)
        .order_by(Note.created_at.desc())   # newest first
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return make_json_response({
        "notes": notes_schema.dump(paginated.items),
        "total": paginated.total, # total number of notes
        "page": paginated.page, # current page
        "pages": paginated.pages, # total number of pages
        "per_page": paginated.per_page
    }, 200)


@app.route("/notes/<int:id>", methods=["GET"])
def get_note(id):

    if not request.current_user:
        return make_json_response({"error": "You must be logged in."}, 401)

    note = db.session.get(Note, id)

    # Note doesn't exist
    if not note:
        return make_json_response({"error": f"Note with id {id} not found."}, 404)

    # Note exists but belongs to someone else
    if note.user_id != request.current_user.id:
        return make_json_response({"error": "Access denied."}, 403)

    return make_json_response(note_schema.dump(note), 200)


@app.route("/notes", methods=["POST"])
def create_note():

    if not request.current_user:
        return make_json_response({"error": "You must be logged in."}, 401)

    data = request.get_json()

    # Validate the data with marshmallow
    try:
        validated_data = note_schema.load(data)
    except ValidationError as err:
        return make_json_response({"errors": err.messages}, 422)

    # Create the note and link it to the logged-in user
    new_note = Note(
        title=validated_data["title"],
        content=validated_data["content"],
        user_id=request.current_user.id  # automatically set from session
    )

    db.session.add(new_note)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_json_response({"error": str(e)}, 500)

    return make_json_response(note_schema.dump(new_note), 201)


@app.route("/notes/<int:id>", methods=["PATCH"])
def update_note(id):
 
    if not request.current_user:
        return make_json_response({"error": "You must be logged in."}, 401)

    note = db.session.get(Note, id)

    if not note:
        return make_json_response({"error": f"Note with id {id} not found."}, 404)

    if note.user_id != request.current_user.id:
        return make_json_response({"error": "Access denied."}, 403)

    data = request.get_json()

    try:
        validated_data = note_schema.load(data, partial=True)
    except ValidationError as err:
        return make_json_response({"errors": err.messages}, 422)

    # Update only the fields that were provided
    if "title" in validated_data:
        note.title = validated_data["title"]
    if "content" in validated_data:
        note.content = validated_data["content"]

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_json_response({"error": str(e)}, 500)

    return make_json_response(note_schema.dump(note), 200)


@app.route("/notes/<int:id>", methods=["DELETE"])
def delete_note(id):

    if not request.current_user:
        return make_json_response({"error": "You must be logged in."}, 401)

    note = db.session.get(Note, id)

    if not note:
        return make_json_response({"error": f"Note with id {id} not found."}, 404)

    if note.user_id != request.current_user.id:
        return make_json_response({"error": "Access denied."}, 403)

    db.session.delete(note)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_json_response({"error": str(e)}, 500)

    return make_json_response({}, 204)


if __name__ == "__main__":
    app.run(port=5555, debug=True)