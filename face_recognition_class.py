import sys
import cv2
import numpy as np
import face_recognition
import math
import time
import tkinter as tk
from tkinter import messagebox
import threading
import os
from register_person import register_person
from database import recognize_students

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
        self.recognized_students = []  # Array to store recognized student names

        # Initialize a dictionary to track the identification time for each face
        self.identification_times = {}

        self.buttons = []  # Inicializa a lista de botões

        self.encode_faces()

    def encode_faces(self):
        self.disable_buttons()
        self.show_timed_popup("Treinamento", "Treinando o modelo. Por favor, aguarde...")
        if not os.path.exists(self.faces_dir):
            print(f"Directory {self.faces_dir} does not exist.")
            messagebox.showerror("Erro", f"Diretório {self.faces_dir} não existe.")
            self.enable_buttons()
            return

        self.known_face_encodings = []
        self.known_face_names = []

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
        self.show_timed_popup("Treinamento", "Modelo treinado com sucesso!")
        self.enable_buttons()

    def run_recognition(self):
        self.disable_buttons()
        self.show_timed_popup("Reconhecimento", "Iniciando o reconhecimento facial. Por favor, aguarde...")
        video_capture = cv2.VideoCapture(self.video_source)
        if not video_capture.isOpened():
            sys.exit('Video source not found...')
        self.recognized_students = []
        start_time = time.time()
        recognized_in_this_run = False  # Track if anyone was recognized in this run

        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to capture image")
                break
            frame = cv2.flip(frame, 1)
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

                        # Add or update the identification time for this face
                        if name in self.identification_times:
                            self.identification_times[name]['count'] += 1
                        else:
                            self.identification_times[name] = {'count': 1, 'time': time.time()}

                        # Check if the face has been identified for at least 3 seconds (90 frames if processing every frame)
                        if self.identification_times[name]['count'] >= 10:
                            # Add the recognized name to the recognized_students array if not already present
                            if name not in self.recognized_students:
                                self.recognized_students.append(name)
                                self.identification_times[name]['count'] = 0  # Reset the count after recognizing
                                recognized_in_this_run = True
                    else:
                        if name in self.identification_times:
                            del self.identification_times[name]

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
        self.enable_buttons()

       
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if(self.recognized_students != []):
            info_text = f"Reconhecido: {self.recognized_students}\nTime: {current_time}"
        else:
            info_text = f"Ninguém reconhecido\nTime: {current_time}"
        
        info_label = tk.Label(self.root, text=info_text, bg='#d9873e', fg='white', font=("Helvetica", 16, "bold"))
        info_label.pack(side=tk.TOP, pady=10)

        # Remove the label after 5 seconds
        self.root.after(5000, info_label.destroy)
        # Print the recognized students
        print("Reconhecido:", self.recognized_students)
        

        # Especificar o caminho do arquivo de banco de dados SQLite
        db_file = "recognition_log.db"

        # Chamar a função para armazenar os dados de reconhecimento no banco de dados
        recognize_students(db_file, self.recognized_students)

     

    def show_timed_popup(self, title, message, duration=2000):
        def show():
            popup = tk.Toplevel(self.root)
            popup.title(title)
            label = tk.Label(popup, text=message)
            label.pack(padx=20, pady=20)
            self.root.after(duration, popup.destroy)
        self.root.after(0, show)

    def disable_buttons(self):
        for button in self.buttons:
            button.config(state=tk.DISABLED)

    def enable_buttons(self):
        for button in self.buttons:
            button.config(state=tk.NORMAL)

    def show_main_buttons(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_main_buttons()

    def create_main_buttons(self):
        canvas = tk.Canvas(self.root, height=600, width=400, bg='#cccccc')
        canvas.pack()

        frame = tk.Frame(self.root, bg='#cccccc')
        frame.place(relwidth=1, relheight=1)

        # Adicionar a imagem no topo
        image = tk.PhotoImage(file="unifil.png")
        image_label = tk.Label(frame, image=image, bg='#cccccc')
        image_label.image = image  # Manter referência para evitar coleta de lixo
        image_label.pack(side=tk.TOP, pady=20)

        # Adicionar texto de instruções
        instructions = (
            "Instruções de cadastro:\n"
            "1. Caso não tenha se cadastrado, clique em Cadastre-se\n"
            "2. Treine o modelo para que sua face seja reconhecida\n"
            "3. Clique em Reconhecimento Facial e fique pelo menos 3 segundos na tela"
        )
        instructions_label = tk.Label(frame, text=instructions, justify="left", bg='#cccccc', font=("Helvetica", 12))
        instructions_label.pack(side=tk.TOP, pady=10)

        self.buttons = []

        register_button = tk.Button(frame, text="Cadastrar Pessoa", padx=20, pady=10, fg="white", bg="#d9873e", font=("Helvetica", 16, "bold"), width=20, command=lambda: register_person(self.root))
        register_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.buttons.append(register_button)

        # Botão para Treinar o Modelo
        train_button = tk.Button(frame, text="Treinar Modelo", padx=20, pady=10, fg="white", bg="#d9873e", font=("Helvetica", 16, "bold"), width=20, command=lambda: threading.Thread(target=self.encode_faces).start())
        train_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.buttons.append(train_button)

        recognize_button = tk.Button(frame, text="Iniciar Reconhecimento", padx=20, pady=10, fg="white", bg="#d9873e", font=("Helvetica", 16, "bold"), width=20, command=lambda: threading.Thread(target=self.run_recognition).start())
        recognize_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.buttons.append(recognize_button)

       

# Código principal para inicializar a interface Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Reconhecimento Facial")
    root.geometry("800x600")
    root.configure(bg='#cccccc')
    app = FaceRecognition(root)
    root.mainloop()
