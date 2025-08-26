import sqlite3
import hashlib

cursor = None
db_name = 'scripts/problems_db.sql'
conn = None
def create_cursor():
    global cursor, conn 
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

def close_cursor():
    global cursor, conn
    cursor.close()
    conn.close()

def create_user_table():
    global cursor, conn
    create_cursor() 
    cursor.execute("""CREATE TABLE IF NOT EXIST USER_TABLE(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERNAME TEXT UNIQUE NOT NULL,
                PASSWORD NVARCHAR NOT NULL
                NAME TEXT NOT NULL
                GRADE INTEGER CHECK(GRADE IN (10,11,12)) NOT NULL
                   )""")
    close_cursor()

def create_subjects_table():
    global cursor, conn
    create_cursor()
    cursor.execute("""CREATE TABLE IF NOT EXIST SUBJECTS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME TEXT UNIQUE NOT NULL)""")
    subject = ['Trigonometry, Algebra', 'Physics', 'Chemistry', 'Computer Science']
    cursor.executemany("INSERT OR IGNORE INTO SUBJECTS (NAME) VALUES (?)", [(s,) for s in subjects])
    conn.commit()
    close_cursor()

def create_tasks_table():
    global cursor, conn
    create_cursor()
    cursor.execute("""CREATE TABLE IF NOT EXIST TASKS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                TITLES TEXT UNIQUE NOT NULL,
                DESCRIPTION TEXT,
                GRADE INTEGER CHECK(GRADE IN (10,11,12)) NOT NULL,
                SUBJECT_ID INTEGER NOT NULL,
                FOREIGN KEY(SUBJECT_ID) REFERENCES SUBJECTS(ID))""")
    conn.commit()
    close_cursor()
    
def create_completed_tasks_table():
    global cursor, conn
    create_cursor()
    cursor.execute("""CREATE TABLE IF NOT EXIST COMPLETED_TASKS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID INTEGER NOT NULL,
                TASK_ID INTEGER NOT NULL,
                COMPLETED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(USER_ID) REFERENCES USERS(ID),
                FOREIGN KEY(TASK_ID) REFERENCES TASKS(ID))""")
    conn.commit()
    close_cursor()

def init_db():
    create_user_table()
    create_subjects_table()
    create_tasks_table()
    create_completed_tasks_table()
    
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, name, grade):
    global cursor, conn
    create_cursor()
    try:
        cursor.execute('INSERT INTO USERS (USERNAME, PASSWORD, NAME, GRADE) VALUES(?,?,?,?)',
                       (username,hash_password(password),name,grade))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        close_cursor()

def login_user(username, password):
    global cursor, conn
    create_cursor()
    cursor.execute('SELECT ID, PASSWORD, NAME, GRADE FROM USERS WHERE NAME =?', (username,))
    row = cursor.fetchone()
    close_cursor()
    if row and row[1] == hash_password(password):
        return {'user_id': row[0], 'name': row[2], 'grade' : row[3]}
    return None

def add_problems(title,description, grade, subject_name):
    global cursor, conn
    create_cursor()

    cursor.execute("SELECT ID FROM SUBJECTS WHERE NAME = ?", (subject_name,))
    row = cursor.fetchone()

    if not row:
        close_cursor()
        return False
    subject_id = row[0]
    cursor.execute("INSERT INTO TASKS (TITLE, DESCRIPTION, GRADE, SUBJECT_ID) VALUES(?,?,?,?)")

    conn.commit()
    close_cursor()
    return True