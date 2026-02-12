import cv2
import os
import numpy as np
import json
from datetime import datetime


def generate_dataset(emp_id):

    face_classifier = cv2.CascadeClassifier(
        "haarcascade_frontalface_default.xml")

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return None

        for (x, y, w, h) in faces:
            return img[y:y+h, x:x+w]

    cap = cv2.VideoCapture(0)
    img_id = 0

    folder_path = f"data/{emp_id}"
    os.makedirs(folder_path, exist_ok=True)

    cv2.namedWindow("Register Face", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Register Face", cv2.WND_PROP_TOPMOST, 1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cropped = face_cropped(frame)

        if cropped is not None:
            img_id += 1
            face = cv2.resize(cropped, (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            file_path = f"{folder_path}/{emp_id}.{img_id}.jpg"
            cv2.imwrite(file_path, face)

            cv2.putText(face, f"Count: {img_id}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Register Face", face)

        if img_id >= 100:
            break

        if cv2.waitKey(1) == 13:
            break

    cap.release()
    cv2.destroyAllWindows()


def train_classifier(data_dir):

    faces = []
    ids = []

    for root, dirs, files in os.walk(data_dir):

        folder_name = os.path.basename(root)

        # Skip root "data" folder
        if not folder_name.isdigit():
            continue

        emp_id = int(folder_name)

        for file in files:
            if file.endswith(".jpg"):
                path = os.path.join(root, file)
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

                if img is None:
                    continue

                faces.append(img)
                ids.append(emp_id)

    if len(faces) == 0:
        print("No images found for training")
        return

    ids = np.array(ids)

    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("classifier.xml")

    print("Training Completed")


def recognize_face():

    face_classifier = cv2.CascadeClassifier(
        "haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")

    name_map = {}
    if os.path.exists("employees.json"):
        with open("employees.json", "r") as f:
            name_map = json.load(f)

    cap = cv2.VideoCapture(0)

    cv2.namedWindow("Attendance", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Attendance", cv2.WND_PROP_TOPMOST, 1)

    start_time = cv2.getTickCount()
    marked = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            emp_id, pred = clf.predict(gray[y:y+h, x:x+w])
            confidence = int(100 * (1 - pred/300))

            if confidence > 70:
                name = name_map.get(str(emp_id), "Unknown")

                if not marked:
                    mark_attendance(name)
                    marked = True

                cv2.putText(frame, name, (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Attendance", frame)

        elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        if elapsed > 20:
            break

        if cv2.waitKey(1) == 13:
            break

    cap.release()
    cv2.destroyAllWindows()


def mark_attendance(name):

    file_name = "attendance.csv"

    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("Name,Time,Date\n")

    with open(file_name, "a") as f:
        now = datetime.now()
        dtString = now.strftime("%H:%M:%S")
        dString = now.strftime("%d/%m/%Y")
        f.write(f"{name},{dtString},{dString}\n")
