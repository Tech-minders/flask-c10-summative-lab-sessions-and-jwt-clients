from flask import Flask
from flask_migrate import Migrate
from models import db, bcrypt
app = Flask(__name__)


app = Flask(__name__)

app.config["SECRET_KEY"] = "super-secret-key-change-this-in-production"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(port=5555, debug=True)