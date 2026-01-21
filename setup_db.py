import sqlite3

def init_real_world_db():
    conn = sqlite3.connect('company_data.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY,
            dept_name TEXT NOT NULL,
            location TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            job_title TEXT,
            salary REAL,
            hire_date DATE,
            dept_id INTEGER,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY,
            project_name TEXT,
            budget REAL,
            dept_id INTEGER,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)

    depts = [
        (1, 'Engineering', 'Riyadh'),
        (2, 'Sales', 'Jeddah'),
        (3, 'Data Science', 'Riyadh'),
        (4, 'HR', 'Dammam')
    ]
    
    employees = [
        (101, 'Ahmed Mansour', 'Software Engineer', 12000, '2022-01-15', 1),
        (102, 'Sara Al-Otaibi', 'Data Analyst', 15000, '2021-06-10', 3),
        (103, 'Khalid Al-Fahad', 'Sales Manager', 11000, '2023-03-20', 2),
        (104, 'Laila Hassan', 'HR Specialist', 9000, '2020-11-05', 4),
        (105, 'Omar Bakri', 'ML Engineer', 16500, '2022-09-12', 3)
    ]

    projects = [
        (501, 'AI Chatbot', 50000, 3),
        (502, 'E-commerce App', 120000, 1),
        (503, 'Cloud Migration', 80000, 1)
    ]

    cursor.executemany("INSERT OR IGNORE INTO departments VALUES (?,?,?)", depts)
    cursor.executemany("INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?,?)", employees)
    cursor.executemany("INSERT OR IGNORE INTO projects VALUES (?,?,?,?)", projects)

    conn.commit()
    conn.close()
    print("✅ Database 'company_data.db' created successfully with relations!")

if __name__ == "__main__":
    init_real_world_db()