from flask import Flask, request, redirect, url_for, session
import sqlite3

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
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT,
        checkin TEXT,
        checkout TEXT,
        room_type TEXT,
        guests INTEGER,
        status TEXT DEFAULT 'Confirmed',
        booked_by TEXT
    );
    """)
    cursor.execute("DELETE FROM hotel_info")
    cursor.execute("""INSERT OR IGNORE INTO hotel_info 
        (hotel_id, hotel_name, location, director, manager, total_rooms) 
        VALUES (1, 'Francois Resort and Spur', 'Mombasa next to Club Volume', 'Francis Mbugua', 'Joseph Kamaru', 350)""")
    
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
    :root { --primary: #1e88e5; --dark: #0d47a1; }
    * { margin:0; padding:0; box-sizing:border-box; font-family: 'Segoe UI', sans-serif; }
    body { background: #f5f7fa; }
    .sidebar { width: 260px; background: white; height: 100vh; position: fixed; box-shadow: 2px 0 10px rgba(0,0,0,0.1); }
    .main-content { margin-left: 260px; padding: 30px; }
    .card { background: white; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); padding: 25px; }
</style>
"""

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
                <p style="color:#666;">and Spur</p>
                <form method="post">
                    <input type="text" name="username" placeholder="Username" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
                    <input type="password" name="password" placeholder="Password" required style="width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
                    <button type="submit" style="width:100%;padding:14px;background:var(--primary);color:white;border:none;border-radius:8px;">Login</button>
                </form>
            </div>
        </div>
    '''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hotel_info")
    hotel = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]
    conn.close()
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
                    <a href="/booking" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">🛎️ New Booking</a>
                    <a href="/bookings" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">📋 All Bookings</a>
                    <a href="/staff" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">👥 Staff & Interns</a>
                    <a href="/logout" style="display:block;padding:12px 15px;color:#d32f2f;border-radius:8px;margin:5px 0;text-decoration:none;">🚪 Logout</a>
                </div>
            </div>
            <div class="main-content">
                <h1>Welcome back, {session['full_name']} 👋</h1>
                <p>{hotel[2]}</p>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:30px;">
                    <div class="card"><h2>{hotel[5]}</h2><p>Total Rooms</p></div>
                    <div class="card"><h2>{total_bookings}</h2><p>Active Bookings</p></div>
                    <div class="card"><h2>92%</h2><p>Occupancy</p></div>
                </div>
            </div>
        </div>
    '''

@app.route('/staff', methods=['GET', 'POST'])
def staff_management():
    if 'username' not in session: return redirect(url_for('login'))
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form['full_name']
        conn = sqlite3.connect("francois_resort.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)", (username, password, role, full_name))
            conn.commit()
            message = "✅ Staff/Intern added successfully!"
        except:
            message = "❌ Username already exists!"
        conn.close()
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, username, role FROM users")
    staff_list = cursor.fetchall()
    conn.close()
    staff_rows = "".join([f"<tr><td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td></tr>" for s in staff_list])
    return f'''
        {SHARED_STYLES}
        <div style="display:flex;height:100vh;">
            <div class="sidebar">
                <div style="padding:25px;border-bottom:1px solid #eee;">
                    <h2 style="color:var(--dark);">Francois Resort</h2>
                </div>
                <div style="padding:20px;">
                    <a href="/dashboard" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">📊 Dashboard</a>
                    <a href="/booking" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">🛎️ New Booking</a>
                    <a href="/bookings" style="display:block;padding:12px 15px;color:#333;border-radius:8px;margin:5px 0;text-decoration:none;">📋 Bookings</a>
                    <a href="/staff" style="display:block;padding:12px 15px;background:#e3f2fd;color:var(--dark);border-radius:8px;margin:5px 0;text-decoration:none;">👥 Staff & Interns</a>
                    <a href="/logout" style="display:block;padding:12px 15px;color:#d32f2f;border-radius:8px;margin:5px 0;text-decoration:none;">🚪 Logout</a>
                </div>
            </div>
            <div class="main-content">
                <h1>Staff & Interns Management</h1>
                {f'<p style="color:green;">{message}</p>' if message else ''}
                <div class="card" style="max-width:700px;">
                    <h2>Add New Staff / Intern</h2>
                    <form method="POST">
                        <input type="text" name="full_name" placeholder="Full Name" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
                        <input type="text" name="username" placeholder="Username (for login)" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
                        <input type="text" name="password" placeholder="Password" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
                        <select name="role" style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
                            <option value="Receptionist">Receptionist</option>
                            <option value="Housekeeping">Housekeeping</option>
                            <option value="Intern">Intern</option>
                            <option value="Cashier">Cashier</option>
                            <option value="Waiter">Waiter</option>
                            <option value="Manager">Manager</option>
                        </select>
                        <button type="submit" style="width:100%;padding:14px;background:#1e88e5;color:white;border:none;border-radius:8px;margin-top:10px;">Add Staff / Intern</button>
                    </form>
                </div>
                <h2 style="margin-top:30px;">Current Staff & Interns</h2>
                <table style="width:100%;border-collapse:collapse;">
                    <tr style="background:#f0f0f0;"><th>Name</th><th>Username</th><th>Role</th></tr>
                    {staff_rows}
                </table>
            </div>
        </div>
    '''

@app.route('/booking')
def booking():
    if 'username' not in session: return redirect(url_for('login'))
    guest_photo = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400"
    return f'''
        {SHARED_STYLES}
        <style>.booking-container {{display:flex;min-height:100vh;}} .guest-sidebar {{width:380px;background:white;padding:40px 25px;box-shadow:3px 0 15px rgba(0,0,0,0.1);text-align:center;}} .avatar {{width:170px;height:170px;border-radius:50%;overflow:hidden;border:6px solid #1e88e5;margin:0 auto 20px;}} .avatar img {{width:100%;height:100%;object-fit:cover;}}</style>
        <div class="booking-container">
            <div class="guest-sidebar">
                <div class="avatar"><img src="{guest_photo}" alt="Guest"></div>
                <h2>Emily Wanjiku</h2>
                <p style="color:#666;">emily.wanjiku@gmail.com</p>
                <p style="color:#666;">📞 +254 711 234 567</p>
                <p style="color:#1e88e5;font-weight:bold;margin-top:30px;">✓ Verified Guest</p>
            </div>
            <div style="flex:1;padding:40px;">
                <div class="card" style="max-width:700px;">
                    <h1>New Guest Booking</h1>
                    <p>Francois Resort and Spur • Mombasa</p>
                    <form method="POST" action="/confirm_booking">
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                            <div><label>Check-in</label><input type="date" name="checkin" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;"></div>
                            <div><label>Check-out</label><input type="date" name="checkout" required style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;"></div>
                        </div>
                        <label>Room Type</label>
                        <select name="room_type" style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
                            <option>Deluxe Room</option><option>Junior Suite</option><option>Presidential Suite</option>
                            <option>Standard Room</option><option>Twin Room</option><option>Double Room</option><option>Suite</option>
                        </select>
                        <label>Number of Guests</label>
                        <input type="number" name="guests" value="2" min="1" style="width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:8px;">
                        <button type="submit" style="width:100%;padding:16px;background:#1e88e5;color:white;border:none;border-radius:8px;margin-top:20px;">Confirm Booking</button>
                    </form>
                </div>
            </div>
        </div>
    '''

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    if 'username' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO bookings (guest_name, checkin, checkout, room_type, guests, booked_by) VALUES (?, ?, ?, ?, ?, ?)""", 
                   ("Emily Wanjiku", request.form['checkin'], request.form['checkout'], request.form['room_type'], request.form['guests'], session['full_name']))
    conn.commit()
    conn.close()
    return '''<h2 style="text-align:center;margin-top:100px;color:#1e88e5;">✅ Booking Confirmed Successfully!</h2>
              <p style="text-align:center;"><a href="/dashboard">← Back to Dashboard</a></p>'''

@app.route('/bookings')
def bookings():
    if 'username' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY booking_id DESC")
    all_bookings = cursor.fetchall()
    conn.close()
    rows = "".join([f"<tr><td>{b[0]}</td><td>{b[1]}</td><td>{b[2]}</td><td>{b[3]}</td><td>{b[4]}</td><td>{b[5]}</td></tr>" for b in all_bookings])
    return f'''
        {SHARED_STYLES}
        <h1>All Bookings</h1>
        <table style="width:100%;border-collapse:collapse;">
            <tr style="background:#f0f0f0;"><th>ID</th><th>Guest</th><th>Check-in</th><th>Check-out</th><th>Room</th><th>Guests</th></tr>
            {rows}
        </table>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)