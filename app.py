from flask import Flask, render_template, request, redirect, session
import os
from werkzeug.utils import secure_filename
import joblib
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


try:
    model = joblib.load("face_shape_model.pkl")
    print("Model loaded successfully")
except:
    model = None



def predict_face_shape(image_path):
    if model is None:
        import random
        return random.choice(["oval", "round", "square", "heart", "diamond"])

    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face = gray[y:y+h, x:x+w]
        else:
            face = gray

        face = cv2.resize(face, (100, 100))
        face = face.flatten().reshape(1, -1)

        return model.predict(face)[0]

    except:
        import random
        return random.choice(["oval", "round", "square", "heart", "diamond"])


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user_id"] = 1
        return redirect("/upload")
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        file = request.files["image"]
        gender = request.form.get("gender")

        if file.filename == "":
            return "No file selected"

        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        face_shape = predict_face_shape(filepath)

        
        if face_shape == "round":
            frames = ["Rectangular", "Square"]
        elif face_shape == "square":
            frames = ["Round", "Oval"]
        elif face_shape == "heart":
            frames = ["Aviator", "Round"]
        elif face_shape == "oval":
            frames = ["Any Frame"]
        elif face_shape == "diamond":
            frames = ["Oval", "Rimless"]
        else:
            frames = ["Standard Frame"]

       
        if gender == "male":
            ornaments = "Watch"
        else:
            if face_shape == "round":
                ornaments = "Long Earrings"
            elif face_shape == "square":
                ornaments = "Hoops"
            elif face_shape == "heart":
                ornaments = "Statement Earrings"
            elif face_shape == "oval":
                ornaments = "Stud Earrings"
            elif face_shape == "diamond":
                ornaments = "Drop Earrings"
            else:
                ornaments = "Minimal Accessories"

       
        frame_images = {
            "Rectangular": "https://i.imgur.com/8Km9tLL.png",
            "Square": "https://i.imgur.com/3Y1qQ0F.png",
            "Round": "https://i.imgur.com/V3KQZ8p.png",
            "Oval": "https://i.imgur.com/2nCt3Sb.png",
            "Aviator": "https://i.imgur.com/6X4ZC9K.png",
            "Any Frame": "https://i.imgur.com/8Km9tLL.png",
            "Standard Frame": "https://i.imgur.com/3Y1qQ0F.png",
            "Rimless": "https://i.imgur.com/9pXnK3T.png"
        }

        
        ornament_images = {
            "Long Earrings": "https://i.imgur.com/1Q9Z1Zm.png",
            "Hoops": "https://i.imgur.com/W6XwX6T.png",
            "Statement Earrings": "https://i.imgur.com/Y3hFQkT.png",
            "Stud Earrings": "https://i.imgur.com/dpKQ8G5.png",
            "Minimal Accessories": "https://i.imgur.com/dpKQ8G5.png",
            "Drop Earrings": "https://i.imgur.com/1Q9Z1Zm.png",
            "Watch": "https://cdn-icons-png.flaticon.com/512/2920/2920322.png"  
        }

        return render_template(
            "result.html",
            image_path="/static/uploads/" + filename,
            face_shape=face_shape.upper(),
            frames=frames,
            ornaments=ornaments,
            frame_images=frame_images,
            ornament_images=ornament_images
        )

    return render_template("upload.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)