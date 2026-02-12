from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
import json
import os
import functions

app = Flask(__name__)

DEPT_API = "https://hrmsapi.leanxpert.in/api/Department"
DESIG_API = "https://hrmsapi.leanxpert.in/api/Designation"
EMP_API = "https://hrmsapi.leanxpert.in/api/Employment"


@app.route("/")
def home():
    try:
        departments = requests.get(DEPT_API).json()
    except:
        departments = []

    return render_template("index.html", departments=departments)


@app.route("/designations/<int:dept_id>")
def get_designations(dept_id):
    try:
        designations = requests.get(DESIG_API).json()
        filtered = [d for d in designations if d["deptId"] == dept_id]
    except:
        filtered = []

    return jsonify(filtered)


@app.route("/employees/<int:dept_id>/<int:desig_id>")
def get_employees(dept_id, desig_id):
    try:
        employees = requests.get(EMP_API).json().get("data", [])
        filtered = [
            e for e in employees
            if e["departmentId"] == dept_id and e["designationId"] == desig_id
        ]
    except:
        filtered = []

    return jsonify(filtered)


@app.route("/register", methods=["POST"])
def register():

    emp_id = request.form.get("empId")
    emp_name = request.form.get("empName")

    mapping_file = "employees.json"
    data = {}

    if os.path.exists(mapping_file):
        with open(mapping_file, "r") as f:
            data = json.load(f)

    data[emp_id] = emp_name

    with open(mapping_file, "w") as f:
        json.dump(data, f, indent=4)

    functions.generate_dataset(emp_id)
    functions.train_classifier("data")

    return redirect(url_for("home"))


@app.route("/attendance", methods=["POST"])
def attendance():
    functions.recognize_face()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
