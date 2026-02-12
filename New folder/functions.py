import cv2
import os
import numpy as np
from PIL import Image
import requests
from datetime import datetime
import csv

# This forces the script to use the folder it is saved in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def upload_to_azure(employee_id, image_name, image_array):
    container_url = "https://staticwebtoken.blob.core.windows.net/employefaceimage"
    sas_token = "?sp=racwdl&st=2026-02-06T05:46:25Z&se=2026-03-31T14:01:25Z&sv=2024-11-04&sr=c&sig=Tho4gf2UIIwkG4WEayxCFFz7KBjum4U8WjrOvdAyb2A%3D"

    success, encoded_image = cv2.imencode(".jpg", image_array)
    if not success:
        print("Image encoding failed")
        return False

    # This creates folder: employefaceimage/87/
    blob_path = f"{employee_id}/{image_name}"
    blob_url = f"{container_url}/{blob_path}{sas_token}"

    headers = {
        "x-ms-blob-type": "BlockBlob",
        "Content-Type": "image/jpeg"
    }

    response = requests.put(
        blob_url,
        data=encoded_image.tobytes(),
        headers=headers
    )

    if response.status_code not in [200, 201]:
        print("Azure upload failed:", response.text)
        return False

    return True

# Automatically create the Data folder if it's missing
# if not os.path.exists("Data"):
#     os.makedirs("Data")
    
# Sync with your HRMS API
def get_employee_name(emp_id):
    try:
        response = requests.get("https://hrmsapi.leanxpert.in/api/Employment")
        emp_data = response.json().get("data", [])
        for emp in emp_data:
            if emp["employmentId"] == emp_id:
                return emp["empName"]
    except:
        return "Unknown User"
    return "Unknown User"

def generate_dataset():
    face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    img_id = 0
    # Note: In a real UI, you'd pass the actual ID from the dropdown here
    user_id = 87 
    
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            img_id += 1
            face = cv2.resize(frame[y:y+h, x:x+w], (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            image_name = f"user.{user_id}.{img_id}.jpg"
             # 🔥 Upload instead of saving locally
            upload_to_azure(user_id, image_name, face)
            # cv2.imwrite(f"Data/user.{user_id}.{img_id}.jpg", face)
            cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Collecting Samples", face)
            
        if cv2.waitKey(1) == 13 or img_id == 100:
            break
    cap.release()
    cv2.destroyAllWindows()

def train_classifier():
    path = [os.path.join("Data", f) for f in os.listdir("Data") if f.endswith(".jpg")]
    faces, ids = [], []
    for image in path:
        img = Image.open(image).convert('L')
        faces.append(np.array(img, 'uint8'))
        ids.append(int(os.path.split(image)[1].split(".")[1]))
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, np.array(ids))
    clf.write("classifier.xml")

def start_attendance():
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = faceCascade.detectMultiScale(gray, 1.1, 10)
        
        for (x, y, w, h) in features:
            id_pred, conf = clf.predict(gray[y:y+h, x:x+w])
            # Sync recognition with API name
            name = get_employee_name(id_pred) if conf < 100 else "Unknown"
            
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 2)
            cv2.putText(img, name, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
            
            # Send to your local Attendance API
            requests.post("http://127.0.0.1:5001/mark_attendance", json={"name": name})

        cv2.imshow("Attendance System", img)
        if cv2.waitKey(1) == 13: break
    cap.release()
    cv2.destroyAllWindows()