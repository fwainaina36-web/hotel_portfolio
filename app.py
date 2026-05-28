from flask import Flask, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'francois_resort_secret_key_2026'

def init_db():
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        full_name TEXT
    );
    CREATE TABLE IF NOT EXISTS hotel_info (
        hotel_id INTEGER PRIMARY KEY,
        hotel_name TEXT,
        location TEXT,
        director TEXT,
        manager TEXT,
        total_rooms INTEGER
    );
    CREATE TABLE IF NOT EXISTS rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE,
        room_type TEXT,
        status TEXT DEFAULT 'Available'
    );
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT,
        checkin TEXT,
        checkout TEXT,
        room_type TEXT,
        guests INTEGER,
        status TEXT DEFAULT 'Confirmed',
        booked_by TEXT,
        booking_date TEXT
    );
    """)
    
    cursor.execute("DELETE FROM hotel_info")
    cursor.execute("""INSERT OR IGNORE INTO hotel_info 
        VALUES (1, 'Francois Resort and Spur', 'Mombasa next to Club Volume', 'Francis Mbugua', 'Joseph Kamaru', 350)""")
    
    cursor.execute("DELETE FROM rooms")
    room_types = ["Deluxe Room", "Junior Suite", "Presidential Suite", "Standard Room", "Twin Room", "Double Room"]
    for i in range(1, 51):
        cursor.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, ?)", 
                      (f"R{str(i).zfill(3)}", room_types[i % len(room_types)]))
    
    cursor.execute("DELETE FROM users")
    cursor.executemany("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)", [
        ("Francis Mbugua", "FM@2026", "Director", "Francis Mbugua"),
        ("Joseph Kamaru", "JK@2026", "Manager", "Joseph Kamaru"),
        ("reception", "reception123", "Receptionist", "Reception Staff")
    ])
    
    conn.commit()
    conn.close()

init_db()

SHARED_STYLES = """
<style>
    :root { --primary: #1e88e5; --dark: #0d47a1; --success: #4CAF50; }
    * { margin:0; padding:0; box-sizing:border-box; font-family: 'Segoe UI', sans-serif; }
    body { background: #f5f7fa; }
    .sidebar { width: 260px; background: white; height: 100vh; position: fixed; box-shadow: 2px 0 10px rgba(0,0,0,0.1); overflow-y:auto; }
    .main-content { margin-left: 260px; padding: 30px; }
    .card { background: white; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); padding: 25px; margin-bottom: 20px; }
    .avatar { width: 170px; height: 170px; border-radius: 50%; overflow: hidden; border: 6px solid #1e88e5; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
    .avatar img { width: 100%; height: 100%; object-fit: cover; }
</style>
"""

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("francois_resort.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = user[1]
            session['role'] = user[3]
            session['full_name'] = user[4]
            return redirect(url_for('dashboard'))
        else:
            return "<h3 style='color:red;text-align:center;margin-top:50px'>Invalid credentials!</h3>"
    return f'''
        {SHARED_STYLES}
        <div style="height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1e88e5,#0d47a1);">
            <div class="card" style="width:400px;padding:40px;text-align:center;">
                <h1 style="color:var(--dark);">🏨 Francois Resort</h1>
                <p style="color:#666;">and Spur - Mombasa</p>
                <form method="post">
                    <input type="text" name="username" placeholder="Username" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
                    <input type="password" name="password" placeholder="Password" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
                    <button type="submit" style="width:100%;padding:14px;background:var(--primary);color:white;border:none;border-radius:8px;">Login</button>
                </form>
            </div>
        </div>
    '''

# Dashboard with Management Face
@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hotel_info")
    hotel = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'")
    available_rooms = cursor.fetchone()[0]
    conn.close()
    
    director_photo = "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400"  # Professional management look
    
    return f'''
        {SHARED_STYLES}
        <div style="display:flex;height:100vh;">
            <div class="sidebar">
                <div style="padding:25px;border-bottom:1px solid #eee;">
                    <h2 style="color:var(--dark);">Francois Resort</h2>
                    <small>Mombasa • 5-Star</small>
                </div>
                <div style="padding:20px;">
                    <a href="/dashboard" style="display:block;padding:12px 15px;background:#e3f2fd;color:var(--dark);border-radius:8px;margin:5px 0;text-decoration:none;">📊 Dashboard</a>
                    <a href="/rooms" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">🛏️ Rooms</a>
                    <a href="/booking" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">🛎️ New Booking</a>
                    <a href="/bookings" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">📋 All Bookings</a>
                    <a href="/staff" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">👥 Staff & Interns</a>
                    <a href="/logout" style="display:block;padding:12px 15px;color:#d32f2f;border-radius:8px;margin:5px 0;text-decoration:none;">🚪 Logout</a>
                </div>
            </div>
            <div class="main-content">
                <div style="display:flex;align-items:center;gap:20px;margin-bottom:30px;">
                    <div class="avatar" style="width:90px;height:90px;border:4px solid var(--primary);">
                        <img src="{director_photo}" alt="Director">
                    </div>
                    <div>
                        <h1>Welcome back, {session['full_name']}</h1>
                        <p style="color:#666;">Hotel Director</p>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;">
                    <div class="card"><h2>{hotel[5]}</h2><p>Total Rooms</p></div>
                    <div class="card"><h2>{available_rooms}</h2><p>Available Rooms</p></div>
                    <div class="card"><h2>{total_bookings}</h2><p>Active Bookings</p></div>
                </div>
            </div>
        </div>
    '''

# Other routes (Staff, Rooms, Booking, etc.) are included in full version. 
# For now, this is the core.

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)