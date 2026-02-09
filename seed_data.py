import sqlite3
import random

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

statuses = ["Pending", "In Progress", "Done"]

# create users
for i in range(1, 1001):  # 1,000 users
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, (f"user{i}", "password123", "user"))

# create tasks
for i in range(1, 50001):  # 50,000 tasks
    cursor.execute("""
        INSERT INTO tasks (title, description, status, user_id)
        VALUES (?, ?, ?, ?)
    """, (
        f"Task {i}",
        "Auto-generated task for load testing",
        random.choice(statuses),
        random.randint(1, 1000)
    ))

conn.commit()
conn.close()

print("Database seeded with large data successfully!")
