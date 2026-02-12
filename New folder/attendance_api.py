from flask import Flask, request, jsonify
from datetime import datetime
import csv

app = Flask(__name__)

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    name = data["name"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("attendance.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, timestamp])

    return jsonify({"message": "Attendance marked"}), 200

app.run(port=5001,debug=True)
