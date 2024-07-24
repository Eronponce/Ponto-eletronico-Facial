import os
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def capture_photos(person_dir, root):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Não foi possível acessar a câmera.")
        return

    def take_photo():
        nonlocal count
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Não foi possível capturar a imagem.")
            return

        img_name = os.path.join(person_dir, f"img_{count}.png")
        cv2.imwrite(img_name, frame)
        count += 1
        print(f"{img_name} escrito!")

    def close_camera():
        cap.release()
        cv2.destroyAllWindows()
        top.destroy()
        messagebox.showinfo("Info", "Fotos capturadas com sucesso!")

    top = tk.Toplevel(root)
    top.title("Capture Photos")

    count = 0

    lmain = tk.Label(top)
    lmain.pack()

    def show_frame():
        ret, frame = cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
        lmain.after(10, show_frame)

    show_frame()

    btn_frame = tk.Frame(top)
    btn_frame.pack()

    take_photo_button = tk.Button(btn_frame, text="Tirar Foto", command=take_photo, fg="white", bg="#4CAF50", font=("Helvetica", 12, "bold"))
    take_photo_button.pack(side=tk.LEFT, padx=10, pady=10)

    finish_button = tk.Button(btn_frame, text="Finalizar", command=close_camera, fg="white", bg="#F44336", font=("Helvetica", 12, "bold"))
    finish_button.pack(side=tk.RIGHT, padx=10, pady=10)
