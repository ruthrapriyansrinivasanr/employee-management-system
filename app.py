from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "employees.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            salary REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    conn = get_db()
    if search:
        employees = conn.execute(
            """SELECT * FROM employees
               WHERE name LIKE ? OR department LIKE ? OR email LIKE ?
               ORDER BY id DESC""",
            (f"%{search}%", f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        employees = conn.execute(
            "SELECT * FROM employees ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return render_template("index.html", employees=employees, search=search)

@app.route("/add", methods=["POST"])
def add_employee():
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    department = request.form["department"].strip()
    salary = request.form["salary"]

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO employees (name, email, department, salary) VALUES (?, ?, ?, ?)",
            (name, email, department, float(salary))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Email already exists. Please use another email.", 400
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    conn = get_db()
    conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    conn = get_db()
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        department = request.form["department"].strip()
        salary = request.form["salary"]
        conn.execute(
            """UPDATE employees
               SET name=?, email=?, department=?, salary=?
               WHERE id=?""",
            (name, email, department, float(salary), employee_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()
    if employee is None:
        return "Employee not found.", 404
    return render_template("edit.html", employee=employee)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
