from extensions import db
from flask_login import UserMixin

# Friend Association Table
friend = db.Table(
    "friends",
    db.Column("friend1_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("friend2_id", db.Integer, db.ForeignKey("user.id")),
)


# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=True)
    posts = db.relationship("Post", back_populates="user", lazy=True)
    friends = db.relationship(
        "User",
        secondary=friend,
        primaryjoin=(friend.c.friend1_id == id),
        secondaryjoin=(friend.c.friend2_id == id),
        backref="friend1",
    )

    def __repr__(self):
        return f"{self.name}"


# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(500), nullable=False)
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="posts")
