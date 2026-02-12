from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

DEPT_API = "https://hrmsapi.leanxpert.in/api/Department"
DESIG_API = "https://hrmsapi.leanxpert.in/api/Designation"
EMP_API = "https://hrmsapi.leanxpert.in/api/Employment"

@app.route("/")
def home():
    departments = requests.get(DEPT_API).json()
    return render_template("index.html", departments=departments)

# 🔹 Get designations by department
@app.route("/designations/<int:dept_id>")
def get_designations(dept_id):
    designations = requests.get(DESIG_API).json()
    filtered = [d for d in designations if d["deptId"] == dept_id]
    return jsonify(filtered)

# 🔹 Get employees by department
@app.route("/employees/<int:dept_id>")
def get_employees(dept_id):
    emp_data = requests.get(EMP_API).json().get("data", [])
    filtered = [e for e in emp_data if e["departmentId"] == dept_id]
    return jsonify(filtered)

if __name__ == "__main__":
    app.run(debug=True)
