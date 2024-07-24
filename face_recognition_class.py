import os
import sys
import cv2
import numpy as np
import face_recognition
import math
import time
import tkinter as tk
from tkinter import messagebox
import threading
from register_person import register_person 
# Helper function to calculate face confidence
def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

class FaceRecognition:
    def __init__(self, root, faces_dir='faces', video_source=0):
        self.root = root
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.known_face_encodings = []
        self.known_face_names = []
        self.process_current_frame = True
        self.faces_dir = faces_dir
        self.video_source = video_source
        self.stop_recognition = False

        self.encode_faces()

    def encode_faces(self):
        if not os.path.exists(self.faces_dir):
            print(f"Directory {self.faces_dir} does not exist.")
            return

        for person_name in os.listdir(self.faces_dir):
            person_dir = os.path.join(self.faces_dir, person_name)
            if not os.path.isdir(person_dir):
                continue
            for image_name in os.listdir(person_dir):
                image_path = os.path.join(person_dir, image_name)
                try:
                    face_image = face_recognition.load_image_file(image_path)
                    face_encoding = face_recognition.face_encodings(face_image)[0]
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(person_name)
                except IndexError:
                    print(f"No face found in the image {image_path}. Skipping.")
                except Exception as e:
                    print(f"Error processing image {image_path}: {str(e)}")

        print("Known faces:", self.known_face_names)

    def run_recognition(self):
        video_capture = cv2.VideoCapture(self.video_source)
        if not video_capture.isOpened():
            sys.exit('Video source not found...')

        start_time = time.time()
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to capture image")
                break

            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    confidence = '???'

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    self.face_names.append(f'{name} ({confidence})')

            self.process_current_frame = not self.process_current_frame

            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) == ord('q') or (time.time() - start_time) > 5:
                break

        video_capture.release()
        cv2.destroyWindow('Face Recognition')

    def show_main_buttons(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_main_buttons()

    def create_main_buttons(self):
        from main import start_recognition

        canvas = tk.Canvas(self.root, height=300, width=400)
        canvas.pack()

        frame = tk.Frame(self.root, bg='white')
        frame.place(relwidth=1, relheight=1)

        register_button = tk.Button(frame, text="Cadastrar Pessoa", padx=10, pady=5, fg="white", bg="#263D42", font=("Helvetica", 12, "bold"), command=lambda: register_person(self, self.root))
        register_button.pack(side=tk.LEFT, expand=True, padx=20, pady=20)

        recognize_button = tk.Button(frame, text="Iniciar Reconhecimento", padx=10, pady=5, fg="white", bg="#263D42", font=("Helvetica", 12, "bold"), command=lambda: threading.Thread(target=self.run_recognition).start())
        recognize_button.pack(side=tk.RIGHT, expand=True, padx=20, pady=20)
