from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Root route to serve index.html
@app.route('/')
def index():
    return render_template('index.html')

# Creating 2 tables
def init_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    # User Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )
    """)

    # Task Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        taskID INTEGER PRIMARY KEY AUTOINCREMENT,
        userID INTEGER,
        title TEXT,
        description TEXT,
        due_date TEXT,
        isCompleted INTEGER DEFAULT 0,
        FOREIGN KEY (userID) REFERENCES users(userID)
    )
    """)

    conn.commit()
    conn.close()

init_db()

# User Endpoints
@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE userID = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (data['name'], data['email']))
    conn.commit()
    conn.close()
    return jsonify({"message": "User added successfully"}), 201

@app.route('/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.json
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ?, email = ? WHERE userID = ?", 
                  (data['name'], data['email'], user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "User updated successfully"}), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE userID = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User deleted successfully"}), 204

# Task Endpoints
@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    is_completed = request.args.get('is_completed')
    user_id = request.args.get('user_id')
    
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND due_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND due_date <= ?"
        params.append(end_date)
    if is_completed is not None:
        query += " AND isCompleted = ?"
        params.append(int(is_completed))
    if user_id:
        query += " AND userID = ?"
        params.append(int(user_id))
    
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE taskID = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (userID, title, description, due_date, isCompleted) 
        VALUES (?, ?, ?, ?, ?)
    """, (data['userID'], data['title'], data['description'], 
          data['due_date'], data.get('isCompleted', 0)))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task added successfully"}), 201

@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    data = request.json
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    if 'isCompleted' in data:
        # If only marking as completed
        cursor.execute("UPDATE tasks SET isCompleted = ? WHERE taskID = ?", 
                      (data['isCompleted'], task_id))
    else:
        # Full update
        cursor.execute("""
            UPDATE tasks 
            SET title = ?, description = ?, due_date = ?, isCompleted = ? 
            WHERE taskID = ?
        """, (data['title'], data['description'], data['due_date'], 
              data.get('isCompleted', 0), task_id))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE taskID = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted successfully"}), 204

if __name__ == '__main__':
    app.run(debug=True)

