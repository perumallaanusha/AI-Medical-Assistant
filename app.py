from gemini_ai import ask_gemini
from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    send_file,
    redirect,
    url_for,
    session
)

import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from disease_info import disease_info
from pdf_report import generate_pdf

app = Flask(__name__)
app.secret_key = "AI_MEDICAL_SECRET_KEY_2026"

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER

# Load trained AI model
model = load_model("skin_disease_model.h5")

# Disease classes
classes = [
    "Acne",
    "Eczema",
    "Healthy Skin",
    "Psoriasis",
    "Ringworm"
]

# Create folders automatically
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(REPORT_FOLDER):
    os.makedirs(REPORT_FOLDER)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# Download PDF Report
@app.route("/download-report")
def download_report():

    pdf_path = os.path.join(
        app.config["REPORT_FOLDER"],
        "Medical_Report.pdf"
    )

    return send_file(
        pdf_path,
        as_attachment=True
    )
@app.route("/history")
def history():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT id,
        date_time,
        symptoms,
        disease,
        confidence
    FROM history
    WHERE username=?
    ORDER BY id DESC
    """,(session["user"],)
    )

    history_data = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=history_data
    )
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users(username,email,password)
                VALUES(?,?,?)
                """,
                (username, email, password)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()
            return "Email already exists!"

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):

            session["user"] = user[1]

            return redirect(url_for("home"))

        else:

            return "Invalid Email or Password"

    return render_template("login.html")
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
     return redirect(url_for("login"))
    result = ""
    symptom = ""
    image_message = ""
    image_filename = ""
    prediction = ""
    confidence = ""
    confidence_bar = ""
    details = None
    ai_response = ""

    if request.method == "POST":

        symptom = request.form.get("symptom", "")
        print("="*50)
        print("Symptom:",repr(symptom))
        print("="*50)
        print("===================================")
        print("Symptom received:", symptom)
        print("Length:", len(symptom))
        print("===================================")
        user_input = symptom.lower()
        uploaded_image = request.files.get("image")
        emergency_keywords = [
          "chest pain",
          "difficulty breathing",
          "unconscious",
          "heavy bleeding",
          "heart attack",
          "stroke",
          "seizure"
       ]  

        if any(word in user_input for word in emergency_keywords):

         result = """
         🚨 EMERGENCY WARNING 🚨

          Your symptoms may indicate a medical emergency.

          • Visit the nearest hospital immediately.
          • Call emergency services.
          • Do not rely only on this AI assistant.

          ⚠ This AI Medical Assistant is for educational purposes only."""

         

        if uploaded_image and uploaded_image.filename != "":

            image_filename = uploaded_image.filename

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                image_filename
            )

            uploaded_image.save(image_path)

            image_message = (
                f"✅ Image uploaded successfully: {image_filename}"
            )

            # ---------------- AI Prediction ----------------

            img = image.load_img(
                image_path,
                target_size=(224, 224)
            )

            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0

            prediction_result = model.predict(
                img_array,
                verbose=0
            )

            predicted_class = np.argmax(prediction_result)

            prediction = classes[predicted_class]

            confidence = round(
                float(np.max(prediction_result)) * 100,
                2
            )

            # Confidence Bar
            filled = int(confidence / 5)
            empty = 20 - filled

            confidence_bar = (
                "█" * filled +
                "-" * empty
            )

            # Disease Details
            details = disease_info.get(prediction)
            # Save prediction to history

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
              """
              INSERT INTO history
              (username, symptoms, disease, confidence, date_time)
               VALUES (?, ?, ?, ?, ?)
              """,
                (
                  session["user"],
                  symptom,
                  prediction,
                  confidence,
                  datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                )
          )  

            conn.commit()
            conn.close()

            # -------- Generate PDF Report --------

            pdf_path = os.path.join(
                app.config["REPORT_FOLDER"],
                "Medical_Report.pdf"
            )

            generate_pdf(
                pdf_path,
                prediction,
                confidence,
                details,
                symptom
            )
        print("Image block finished")
        print("Reached Gemini Block")
        print("Current result=", result)
        print("Result before Gemini=",repr(result))
        if not result:
         try:
          ai_response = ask_gemini(symptom)

         except Exception:

          ai_response = """
         🤖 AI Medical Assistant

Possible Condition:
Your symptoms may indicate a viral infection or seasonal illness.

Precautions:
• Drink plenty of water
• Take proper rest
• Eat nutritious food
• Monitor your temperature

Recommendation:
Please consult a qualified doctor if symptoms continue or worsen.

⚠ This information is for educational purposes only.
"""

    # ---------------- Symptom Analysis ----------------

     # ---------------- Symptom Analysis ----------------

    

    return render_template(
        "index.html",
        result=result,
        symptom=symptom,
        image_message=image_message,
        image_filename=image_filename,
        prediction=prediction,
        confidence=confidence,
        confidence_bar=confidence_bar,
        details=details,
        ai_response=ai_response
    )
@app.route("/delete-history/<int:id>")
def delete_history(id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM history WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("history"))

if __name__ == "__main__":
    app.run(debug=True)