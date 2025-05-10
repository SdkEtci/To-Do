from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)


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
        isCompleted INT, 
        FOREIGN KEY (userID) REFERENCES users(userID)
    )
    """)

    conn.commit()
    conn.close()

init_db()

# GET /users
@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

# GET /users/<id>
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)


# POST /users
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (data['name'], data['email']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Kullanıcı başarılı şekilde eklendi"}), 201

# PUT /users/<id>
@app.route('/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.json
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (data['name'], data['email'], user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Kullanıcı başarılı şekilde güncellendi"}), 200


# DELETE /users/<id>
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Kullanıcı silindi"}), 204

if __name__ == '__main__':
    app.run(debug=True)

