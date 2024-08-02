import os
import re
import tkinter as tk
from tkinter import simpledialog
from capture_photos import capture_photos
from unidecode import unidecode
import sqlite3

def sanitize_folder_name(name):
    # Remove acentos e caracteres especiais
    name = unidecode(name)
    # Substitui caracteres que não são alfanuméricos nem espaços por sublinhados
    name = re.sub(r'[^a-zA-Z0-9\s]', '_', name)
    # Substitui espaços por sublinhados
    name = name.replace(' ', '_')
    return name

def save_to_database(real_name, sanitized_name, course, registration, phone, email):
    conn = sqlite3.connect('recognition_log.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            real_name TEXT NOT NULL,
            sanitized_name TEXT NOT NULL,
            course TEXT,
            registration TEXT,
            phone TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO people (real_name, sanitized_name, course, registration, phone, email) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (real_name, sanitized_name, course, registration, phone, email))
    conn.commit()
    conn.close()

def register_person(root):
    real_name = simpledialog.askstring("Input", "Qual é o nome completo da pessoa?", parent=root)
    if not real_name:
        return
    course = simpledialog.askstring("Input", "Qual é o curso da pessoa?", parent=root)
    if not course:
        return
    registration = simpledialog.askstring("Input", "Qual é a matrícula da pessoa?", parent=root)
    if not registration:
        return
    phone = simpledialog.askstring("Input", "Qual é o celular da pessoa?", parent=root)
    if not phone:
        return
    email = simpledialog.askstring("Input", "Qual é o email da pessoa?", parent=root)
    if not email:
        return

    sanitized_name = sanitize_folder_name(real_name)
    person_dir = os.path.join('faces', sanitized_name)
    os.makedirs(person_dir, exist_ok=True)

    save_to_database(real_name, sanitized_name, course, registration, phone, email)

    capture_photos(person_dir, root)

# Exemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar janela principal
    register_person(root)
    root.mainloop()
