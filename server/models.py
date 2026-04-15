from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

# USER MODEL

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    _password_hash = db.Column(db.String(200), nullable=False)
    notes = db.relationship("Note", back_populates="user", cascade="all, delete-orphan")


    @hybrid_property
    def password(self):
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, plain_text_password):
        self._password_hash = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

    def check_password(self, plain_text_password):
        return bcrypt.check_password_hash(self._password_hash, plain_text_password)

    # Validation 
    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username cannot be blank.")
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters.")
        return value.strip()

    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"


# NOTE MODEL

class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="notes")

    # Validations 
    @validates("title")
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError("Title cannot be blank.")
        if len(value) > 100:
            raise ValueError("Title must be 100 characters or fewer.")
        return value.strip()

    @validates("content")
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError("Content cannot be blank.")
        return value.strip()

    def __repr__(self):
        return f"<Note id={self.id} title='{self.title}' user_id={self.user_id}>"