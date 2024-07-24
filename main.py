import tkinter as tk
import threading
from face_recognition_class import FaceRecognition
from register_person import register_person

def start_recognition(fr, root):
    fr.stop_recognition = False
    root.withdraw()
    threading.Thread(target=fr.run_recognition).start()

def main():
    global root
    root = tk.Tk()
    root.title("Sistema de Reconhecimento Facial")

    global fr
    fr = FaceRecognition(root)  # Inicializa FaceRecognition globalmente
    fr.create_main_buttons()

    root.mainloop()

if __name__ == "__main__":
    main()
