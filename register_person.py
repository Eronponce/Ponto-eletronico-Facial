import os
import tkinter as tk
from tkinter import simpledialog
from capture_photos import capture_photos

def register_person(fr, root):
    name = simpledialog.askstring("Input", "Qual é o nome completo da pessoa?", parent=root)
    if not name:
        return

    person_dir = os.path.join('faces', name)
    os.makedirs(person_dir, exist_ok=True)

    capture_photos(person_dir, root)
    fr.encode_faces()  # Recarregar o modelo após cadastrar novo usuário
