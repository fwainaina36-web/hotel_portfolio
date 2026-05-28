from flask import Flask, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'francois_resort_secret_key_2026'

def init_db():
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, full_name TEXT);
    CREATE TABLE IF NOT EXISTS hotel_info (hotel_id INTEGER PRIMARY KEY, hotel_name TEXT, location TEXT, director TEXT, manager TEXT, total_rooms INTEGER);
    """)
    cursor.execute("DELETE FROM hotel_info")
    cursor.execute("INSERT OR IGNORE INTO hotel_info VALUES (1, 'Francois Resort and Spur', 'Mombasa', 'Francis Mbugua', 'Joseph Kamaru', 350)")
    cursor.execute("DELETE FROM users")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)", 
                   ("Francis Mbugua", "FM@2026", "Director", "Francis Mbugua"))
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "Francis Mbugua" and request.form['password'] == "FM@2026":
            session['username'] = "Francis Mbugua"
            return redirect(url_for('dashboard'))
    return '''<div style="height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#10b981,#0f766e);font-family:Segoe UI;">
        <div style="background:white;padding:50px;border-radius:16px;width:400px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <h1 style="color:#10b981;">Francois Resort</h1>
            <p style="color:#666;margin:10px 0 30px;">Modern Villa Management System</p>
            <form method="post">
                <input type="text" name="username" placeholder="Username" required style="width:100%;padding:14px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
                <input type="password" name="password" placeholder="Password" required style="width:100%;padding:14px;margin:10px 0;border:1px solid #ddd;border-radius:8px;">
                <button type="submit" style="width:100%;padding:16px;background:#10b981;color:white;border:none;border-radius:8px;">Sign In</button>
            </form>
        </div>
    </div>'''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect(url_for('login'))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Francois Resort - Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { margin:0; font-family:Segoe UI; background:#f8fafc; }
            .sidebar { width: 240px; background:#1e2937; color:white; height:100vh; position:fixed; padding:20px 0; }
            .main { margin-left:240px; padding:20px; }
            .card { background:white; border-radius:12px; padding:20px; box-shadow:0 5px 15px rgba(0,0,0,0.08); }
            .topbar { background:white; padding:15px 30px; box-shadow:0 2px 10px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center; }
            .stat-card { padding:20px; border-radius:12px; color:white; text-align:center; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="padding:0 20px;color:#10b981;">Francois Resort</h2>
            <div style="padding:20px;">
                <a href="/dashboard" style="display:block;padding:12px 20px;color:white;background:#10b981;border-radius:8px;margin:8px 0;text-decoration:none;">Dashboard</a>
                <a href="#" style="display:block;padding:12px 20px;color:#cbd5e1;border-radius:8px;margin:8px 0;text-decoration:none;">New Booking</a>
                <a href="#" style="display:block;padding:12px 20px;color:#cbd5e1;border-radius:8px;margin:8px 0;text-decoration:none;">Rooms</a>
                <a href="#" style="display:block;padding:12px 20px;color:#cbd5e1;border-radius:8px;margin:8px 0;text-decoration:none;">Bookings</a>
                <a href="#" style="display:block;padding:12px 20px;color:#cbd5e1;border-radius:8px;margin:8px 0;text-decoration:none;">Staff</a>
            </div>
        </div>
        
        <div class="main">
            <div class="topbar">
                <h2>Dashboard</h2>
                <div>Welcome, Francis Mbugua</div>
            </div>
            
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin:30px 0;">
                <div class="stat-card" style="background:#3b82f6;">872 New Booking</div>
                <div class="stat-card" style="background:#10b981;">285 Schedule Room</div>
                <div class="stat-card" style="background:#f59e0b;">53 Check-in</div>
                <div class="stat-card" style="background:#ef4444;">78 Check-out</div>
            </div>
            
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                <div class="card">
                    <h3>Available Rooms Today</h3>
                    <canvas id="pieChart" height="180"></canvas>
                </div>
                <div class="card">
                    <h3>Reservation Statistics</h3>
                    <canvas id="lineChart" height="180"></canvas>
                </div>
            </div>
        </div>
        
        <script>
            new Chart(document.getElementById('pieChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Occupied', 'Available'],
                    datasets: [{ data: [215, 135], backgroundColor: ['#3b82f6', '#10b981'] }]
                }
            });
            
            new Chart(document.getElementById('lineChart'), {
                type: 'line',
                data: {
                    labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
                    datasets: [
                        { label: 'Bookings', data: [45,52,48,65,72,68,75], borderColor: '#3b82f6', tension: 0.4 },
                        { label: 'Check-ins', data: [28,35,30,42,50,48,55], borderColor: '#10b981', tension: 0.4 }
                    ]
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)