from flask import Flask, render_template, redirect, url_for, request
import functions
import json
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():

    emp_id = request.form.get("empId")
    emp_name = request.form.get("empName")

    # save mapping empId -> name
    mapping_file = "employees.json"
    data = {}

    if os.path.exists(mapping_file):
        with open(mapping_file, "r") as f:
            data = json.load(f)

    data[emp_id] = emp_name

    with open(mapping_file, "w") as f:
        json.dump(data, f, indent=4)

    # call capture and training
    functions.generate_dataset(emp_id)
    functions.train_classifier("data")

    return redirect(url_for("home"))


@app.route("/attendance", methods=["POST"])
def attendance():
    functions.recognize_face()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
