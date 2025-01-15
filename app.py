from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import join_room, leave_room, send, SocketIO
from flask_login import login_required, current_user
import random
from datetime import datetime
from string import ascii_uppercase
from extensions import app, db, socketio
from models import User, Post
from auth.routes import auth
from main.forms import PostForm

app.register_blueprint(auth)

with app.app_context():
    db.create_all()

rooms = {}


def generate_unique_code(length):
    """
    Function that generates a unique
    """
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/home", methods=["POST", "GET"])
@login_required
def home():
    form = PostForm()
    posts = Post.query.all()
    users = User.query.all()
    if form.validate_on_submit():
        new_post = Post(
            data=form.data.data,
            date=datetime.today(),
            user_id=current_user.id,
        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    else:
        return render_template("home.html", form=form, posts=posts, users=users)


@app.route("/chat", methods=["POST", "GET"])
@login_required
def chat():
    session.clear()
    if request.method == "POST":
        name = current_user.username
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if join != False and not code:
            return render_template(
                "chat.html", error="Please enter a room code", code=code, name=name
            )

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template(
                "chat.html", error="Room does not exist.", code=code, name=name
            )

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("chat.html")


@app.route("/room")
@login_required
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])


@app.route("/profile/<user_id>")
@login_required
def profile(user_id):
    user = User.query.get(user_id)

    return render_template("profile.html", user=user)


@app.route("/friend/<user_id>", methods=["POST"])
@login_required
def friend_user(user_id):
    user = User.query.get(user_id)
    current_user.friends.append(user)
    db.session.commit()
    return redirect(url_for("profile", user_id=user.id))


@app.route("/unfriend/<user_id>", methods=["POST"])
@login_required
def unfriend_user(user_id):
    user = User.query.get(user_id)
    current_user.friends.remove(user)
    db.session.commit()
    return redirect(url_for("profile", user_id=user.id))


@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    searchbox = request.form.get("text")
    query = User.query.filter(User.username.contains(f"{searchbox}")).all()
    result = []
    for que in query:
        result.append({"username": que.username})
    if searchbox == "":
        result = None
    return jsonify(result)


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {"name": session.get("name"), "message": data["data"]}
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} left room {room}")


if __name__ == "__main__":
    socketio.run(app, debug=True)
