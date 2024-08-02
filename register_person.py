import os
import re
import tkinter as tk
from tkinter import simpledialog
from capture_photos import capture_photos
from unidecode import unidecode

def sanitize_folder_name(name):
    # Remove acentos e caracteres especiais
    name = unidecode(name)
    # Substitui caracteres que não são alfanuméricos nem espaços por sublinhados
    name = re.sub(r'[^a-zA-Z0-9\s]', '_', name)
    # Substitui espaços por sublinhados
    name = name.replace(' ', '_')
    return name

def register_person(root):
    name = simpledialog.askstring("Input", "Qual é o nome completo da pessoa?", parent=root)
    if not name:
        return

    sanitized_name = sanitize_folder_name(name)
    person_dir = os.path.join('faces', sanitized_name)
    os.makedirs(person_dir, exist_ok=True)

    capture_photos(person_dir, root)

# Exemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar janela principal
    register_person(root)
    root.mainloop()
