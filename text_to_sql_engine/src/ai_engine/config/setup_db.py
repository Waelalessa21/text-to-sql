import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

DB_FILE = Path(__file__).resolve().parents[4] / "data" / "company_data.db"

def random_date(start_year=2018):
    start = date(start_year, 1, 1)
    end = date.today()
    return start + timedelta(days=random.randint(0, (end - start).days))

def init_large_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

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
            employment_type TEXT,
            status TEXT,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY,
            project_name TEXT,
            budget REAL,
            dept_id INTEGER,
            start_date DATE,
            status TEXT,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        )
    """)

    depts = [
        (1, "Engineering", "Riyadh"),
        (2, "Sales", "Jeddah"),
        (3, "Data Science", "Riyadh"),
        (4, "HR", "Dammam"),
        (5, "Finance", "Riyadh"),
        (6, "Marketing", "Jeddah"),
        (7, "Operations", "Dammam"),
        (8, "Legal", "Riyadh")
    ]
    cursor.executemany("INSERT OR IGNORE INTO departments VALUES (?,?,?)", depts)

    first_names = ["Ahmed", "Sara", "Omar", "Laila", "Khalid", "Noura", "Fahad", "Reem"]
    last_names = ["Al-Qahtani", "Al-Otaibi", "Al-Fahad", "Al-Harbi", "Al-Mansour", "Al-Bakr"]
    job_titles = [
        "Software Engineer", "Senior Software Engineer", "Backend Engineer",
        "Data Scientist", "ML Engineer", "DevOps Engineer",
        "Sales Executive", "Sales Lead", "HR Manager", "Recruiter", "Finance Analyst"
    ]
    employment_types = ["Full-time", "Contract"]
    statuses = ["Active", "Resigned"]

    employees = []
    emp_id = 101
    for _ in range(200):
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        job = random.choice(job_titles)
        salary = round(random.uniform(8000, 20000), 2)
        hire_date = random_date()
        dept_id = random.randint(1, len(depts))
        emp_type = random.choice(employment_types)
        status = random.choice(statuses)
        employees.append((emp_id, full_name, job, salary, hire_date, dept_id, emp_type, status))
        emp_id += 1

    cursor.executemany("INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?,?,?,?)", employees)

    projects = []
    project_id = 501
    for i in range(50):
        name = f"Project_{i+1}"
        budget = round(random.uniform(20000, 200000), 2)
        dept_id = random.randint(1, len(depts))
        start_date = random_date()
        status = random.choice(["Active", "Completed"])
        projects.append((project_id, name, budget, dept_id, start_date, status))
        project_id += 1

    cursor.executemany("INSERT OR IGNORE INTO projects VALUES (?,?,?,?,?,?)", projects)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY,
            emp_id INTEGER,
            amount REAL,
            sale_date DATE,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY,
            project_id INTEGER,
            emp_id INTEGER,
            task_name TEXT,
            status TEXT,
            deadline DATE,
            FOREIGN KEY (project_id) REFERENCES projects(project_id),
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    """)

    sales_data = [
        (1, 103, 5000, "2023-10-01"),
        (2, 103, 7000, "2023-11-15"),
        (3, 101, 2000, "2023-12-01"),
    ]
    tasks_data = [
        (1, 501, 102, "Design Model", "Completed", "2023-12-01"),
        (2, 501, 105, "Train Model", "Pending", "2024-01-20"),
        (3, 502, 101, "API Development", "Completed", "2023-11-10"),
    ]

    cursor.executemany("INSERT OR IGNORE INTO sales VALUES (?,?,?,?)", sales_data)
    cursor.executemany("INSERT OR IGNORE INTO tasks VALUES (?,?,?,?,?,?)", tasks_data)

    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' created successfully with large data!")

if __name__ == "__main__":
    init_large_db()
