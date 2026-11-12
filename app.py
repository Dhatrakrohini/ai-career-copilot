
import os
import json
import PyPDF2
import docx

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session

from ai import analyze_resume
from db import engine, Base, SessionLocal
import models


# Load environment variables
load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise ValueError("SECRET_KEY is missing from .env")


# Create database tables
Base.metadata.create_all(bind=engine)


# HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()

    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            existing_user = db.query(models.User).filter_by(
                email=email
            ).first()

            if existing_user:
                return "User already exists"

            user = models.User(
                email=email,
                password=password
            )

            db.add(user)
            db.commit()

            return redirect("/login")

        return render_template("signup.html")

    finally:
        db.close()


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = db.query(models.User).filter_by(
                email=email,
                password=password
            ).first()

            if user:
                session["user"] = user.email
                return redirect("/dashboard")

            return "Invalid credentials"

        return render_template("login.html")

    finally:
        db.close()


# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        user_goal = request.form.get("role")
        uploaded_file = request.files.get("file")
        resume_text = ""

        # Check uploaded file
        if not uploaded_file or uploaded_file.filename == "":
            result = {"error": "Please upload your resume."}

        elif uploaded_file.filename.lower().endswith(".pdf"):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)

                for page in pdf_reader.pages:
                    resume_text += page.extract_text() or ""

            except Exception as e:
                result = {"error": f"PDF error: {str(e)}"}

        elif uploaded_file.filename.lower().endswith(".docx"):
            try:
                doc = docx.Document(uploaded_file)

                for para in doc.paragraphs:
                    resume_text += para.text + "\n"

            except Exception as e:
                result = {"error": f"DOCX error: {str(e)}"}

        else:
            result = {
                "error": "Please upload a PDF or DOCX file."
            }

        # Analyze resume
        if resume_text and user_goal and result is None:
            try:
                result = analyze_resume(resume_text, user_goal)

                # Save report to database
                db = SessionLocal()

                try:
                    user = db.query(models.User).filter_by(
                        email=session["user"]
                    ).first()

                    if user:
                        report = models.Reports(
                            user_id=user.id,
                            resume_text=resume_text,
                            result=json.dumps(result)
                        )

                        db.add(report)
                        db.commit()

                finally:
                    db.close()

            except Exception as e:
                result = {"error": f"AI error: {str(e)}"}

        elif not user_goal and result is None:
            result = {"error": "Please enter your target job role."}

        elif not resume_text and result is None:
            result = {"error": "Could not extract text from your resume."}

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )


# HISTORY
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    try:
        user = db.query(models.User).filter_by(
            email=session["user"]
        ).first()

        if not user:
            return redirect("/login")

        reports = db.query(models.Reports).filter_by(
            user_id=user.id
        ).all()

        parsed_reports = []

        for r in reports:
            try:
                parsed_result = json.loads(r.result)
            except (json.JSONDecodeError, TypeError):
                parsed_result = {}

            parsed_reports.append({
                "resume": r.resume_text,
                "result": parsed_result
            })

        return render_template(
            "history.html",
            reports=parsed_reports
        )

    finally:
        db.close()


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)




# from flask import Flask, render_template, request, redirect, session
# from ai import analyze_resume
# from db import engine, Base, SessionLocal
# #from dotenv import load_dotenv
# import models
# import os
# import json
# import PyPDF2
# import docx
# import os
# from dotenv import load_dotenv
# from flask import Flask, render_template, request, redirect, session

# load_dotenv()

# app = Flask(__name__)

# app.secret_key = os.getenv("SECRET_KEY")

# if not app.secret_key:
#     raise ValueError("SECRET_KEY is missing from .env")


# # Create database tables
# Base.metadata.create_all(bind=engine)

# #Home
# @app.route("/")
# def home():
#     if "user" in session:
#         return redirect("/dashboard")
#     return redirect("/login")

# #SIGNUP
# @app.route("/signup" , methods=["GET" , 'POST'])
# def signup():
#     db = SessionLocal()

#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")

#         existing_user = db.query(models.User).filter_by(email=email).first()
#         if existing_user:
#             return "User already exists"

#         user = models.User(email=email, password=password)
#         db.add(user)
#         db.commit()

#         return redirect("/login")

#     return render_template("/signup.html")

# #LOGIN
# @app.route("/login", methods=["GET" , "POST"])
# def login():
#     db = SessionLocal()


#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")

#         user = db.query(models.User).filter_by(email=email, password=password).first()

#         if user:
#             session["user"] = user.email
#             return redirect("/dashboard")
#         else:
#             return "Invalid credentials"
#     return render_template("login.html")

# #DASHBOARD
# @app.route("/dashboard",methods=["GET","POST"])
# def dashboard():
#     if  "user" not in session:
#         return redirect("/login")
#     result = None

#     if request.method == "POST":
#         user_goal = request.form.get("role")
#         file = request.files.get("file")
#         resume_text =""

#     #File Handling
#     if file and filename != "":
#         if file.filename.endswith(".pdf"):
#             try:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 text = ""
#                 for page in pdf_reader.pages:
#                     text += page.extract_text() or ""
#                 resume_text = text
#             except Exception as e:
#                 result = {"error":f"PDF error: {str(e)}"}

#         elif file.filename.endswith(".docx"):
#             try:
#                 doc = docx.Document(file)
#                 text = ""
#                 for para in doc.paragraphs:
#                     text += para.text +"\n"
#                 resume_text = text
#             except Exception as e:
#                 result = {"error:" f"Docx error:{str(e)}"}

#     if resume_text and user_goal:
#         try:
#             result = analyze_resume(resume_text,user_goal)

#             #save to db
#             db = SessionLocal()
#             user = db.query(models.User).filter_by(email=session["user"]).first()

#             report = models.Reports(
#                 user_id= user.id,
#                 resume_text= resume_text,
#                 results = json.dumps(result)

#             )

#             db.add(report)
#             db.commit()

#         except Exception as e:
#             result = {"error" :f"AI error :{str(e)}"}

#     return render_template(
#         "dashboard.html",
#         user = session["user"],
#         result = result
#     )

# #history
# @app.route("/history")
# def history():
#     if "user" not in session:
#         return redirect("/login")

#     db = SessionLocal()
#     user= db.query(models.User).filter_by(email=session["user"]).first()

#     reports = db.query(models.Report).filter_by(user_id = user.id).all()

# #convet JSON string > dict

#     pasred_reports = []
#     for r in reports:
#         try:
#             pasred_reports = json.loads(r.result)
#         except:
#             pasred_reports= []

#         pasred_reports.append({
#             "resume":r.resume_text,
#             "result":pasred_reports
#         })

#     return render_template("history.html" , reports=pasred_reports)


# #logout
# @app.route("/logout")
# def logout():
#     session.pop("user",None)
#     return redirect("/login")


# if __name__ == "__main__":
#     app.run(debug=True)