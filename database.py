import sqlite3
from datetime import datetime, timedelta

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """ Create a table for storing student recognition logs if it doesn't exist """
    create_table_sql = """CREATE TABLE IF NOT EXISTS recognition_log (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            recognition_time text NOT NULL
                          );"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def insert_recognition(conn, name):
    """ Insert a new recognition log into the recognition_log table """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_sql = '''INSERT INTO recognition_log(name, recognition_time) VALUES(?, ?)'''
    cur = conn.cursor()
    cur.execute(insert_sql, (name, now))
    conn.commit()

def get_last_recognition_time(conn, name):
    """ Get the last recognition time for a given name """
    cur = conn.cursor()
    cur.execute("SELECT recognition_time FROM recognition_log WHERE name = ? ORDER BY recognition_time DESC LIMIT 1", (name,))
    row = cur.fetchone()
    return datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") if row else None

def recognize_students(db_file, recognized_students):
    """ Recognize students and store the recognition time in the database """
    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn)
        for student in recognized_students:
            last_recognition_time = get_last_recognition_time(conn, student)
            if last_recognition_time is None or datetime.now() - last_recognition_time > timedelta(minutes=30):
                insert_recognition(conn, student)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")
