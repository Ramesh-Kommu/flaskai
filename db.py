import sqlite3

# Create a new database or connect to the existing one
conn = sqlite3.connect('nanidb.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Create the userdata table
cursor.execute("""
CREATE TABLE IF NOT EXISTS userdata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    usercreatedDate TEXT NOT NULL,
    userlastloggeddate TEXT,
    userrole TEXT NOT NULL
);
""")

# Create the userQuery table
cursor.execute("""
CREATE TABLE IF NOT EXISTS userQuery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    userQuery TEXT NOT NULL,
    queriedtime TEXT NOT NULL,
    aiResponse TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES userdata (username)
);
""")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
