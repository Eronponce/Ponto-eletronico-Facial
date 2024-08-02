import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import ttk
import os
import re
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
    def on_submit():
        real_name = entry_name.get()
        course = entry_course.get()
        registration = entry_registration.get()
        phone = entry_phone.get()
        email = entry_email.get()

        if not real_name or not course or not registration or not phone or not email:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios")
            return

        sanitized_name = sanitize_folder_name(real_name)
        person_dir = os.path.join('faces', sanitized_name)
        os.makedirs(person_dir, exist_ok=True)

        save_to_database(real_name, sanitized_name, course, registration, phone, email)
        capture_photos(person_dir, root)

        form_window.destroy()

    form_window = tk.Toplevel(root)
    form_window.title("Cadastro de Pessoa")
    form_window.geometry("400x300")  # Aumenta o tamanho da janela

    tk.Label(form_window, text="Nome Completo:").grid(row=0, column=0, padx=20, pady=10)
    entry_name = tk.Entry(form_window, width=30)  # Aumenta a largura do campo de entrada
    entry_name.grid(row=0, column=1, padx=20, pady=10)

    tk.Label(form_window, text="Curso:").grid(row=1, column=0, padx=20, pady=10)
    entry_course = tk.Entry(form_window, width=30)
    entry_course.grid(row=1, column=1, padx=20, pady=10)

    tk.Label(form_window, text="Matrícula:").grid(row=2, column=0, padx=20, pady=10)
    entry_registration = tk.Entry(form_window, width=30)
    entry_registration.grid(row=2, column=1, padx=20, pady=10)

    tk.Label(form_window, text="Celular:").grid(row=3, column=0, padx=20, pady=10)
    entry_phone = tk.Entry(form_window, width=30)
    entry_phone.grid(row=3, column=1, padx=20, pady=10)

    tk.Label(form_window, text="Email:").grid(row=4, column=0, padx=20, pady=10)
    entry_email = tk.Entry(form_window, width=30)
    entry_email.grid(row=4, column=1, padx=20, pady=10)

    submit_button = tk.Button(form_window, text="OK", command=on_submit)
    submit_button.grid(row=5, columnspan=2, pady=20)
# Exemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar janela principal
    register_person(root)
    root.mainloop()
