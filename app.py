from flask import Flask, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_hotel_key'

def init_db():
    conn = sqlite3.connect("prideinn_5star.db")
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, role TEXT);
    CREATE TABLE IF NOT EXISTS hotel_info (hotel_id INTEGER PRIMARY KEY AUTOINCREMENT, hotel_name TEXT, director TEXT, manager TEXT, total_rooms INTEGER, total_staff INTEGER, interns INTEGER, rating TEXT);
    """)
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM hotel_info")
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("Francis Mbugua", "FM@2026", "Hotel Director"))
    cursor.execute("INSERT INTO hotel_info (hotel_name, director, manager, total_rooms, total_staff, interns, rating) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   ("PrideInn Grand Royal Resort & Spa", "Francis Mbugua", "Joseph Kamaru", 350, 200, 70, "5-Star Luxury Hotel"))
    conn.commit()
    conn.close()

init_db()

SHARED_STYLES = """
<style>
    :root { --primary: #4CAF50; --primary-light: #E8F5E9; --dark: #2E7D32; --bg: #F4F6F4; --surface: #FFFFFF; --text: #333333; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
    body { background-color: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
</style>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == "Francis Mbugua" and request.form['password'] == "FM@2026":
            session['username'] = request.form['username']
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Credentials"
    return f'''
        {SHARED_STYLES}
        <div style="display: flex; width: 100vw; height: 100vh; align-items: center; justify-content: center; background-color: var(--bg);">
            <div style="background: var(--surface); width: 100%; max-width: 400px; padding: 40px; border-radius: 16px; border: 1px solid #ddd; text-align: center;">
                <h2>PrideInn Grand Royal</h2>
                <p>Hotel Management System</p><br>
                <form method="post">
                    <input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 12px; margin-bottom: 16px;"><br>
                    <input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 12px; margin-bottom: 20px;"><br>
                    <button type="submit" style="width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">Sign In</button>
                </form>
                <p style="color: red;">{error if error else ""}</p>
            </div>
        </div>
    '''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect("prideinn_5star.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hotel_info")
    hotel = cursor.fetchone()
    conn.close()
    
    features = ["Infinity Pool", "Luxury Spa", "VIP Lounge", "Helipad Access"]
    features_html = "".join([f"<div style='padding: 10px; background: #f9f9f9; border-left: 4px solid var(--primary); margin-bottom:8px;'>{f}</div>" for f in features])
    
    return f'''
        {SHARED_STYLES}
        <div style="width: 260px; background: var(--surface); border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; padding: 24px;">
            <h3 style="color: var(--dark);">Villa System</h3><br>
            <a href="#" style="padding: 12px; background: var(--primary-light); color: var(--dark); border-radius: 8px; text-decoration: none; font-weight: bold;">Dashboard</a>
            <a href="/logout" style="padding: 12px; color: red; text-decoration: none; margin-top: auto;">Sign Out</a>
        </div>
        <div style="flex-grow: 1; padding: 40px; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 32px;">
                <div>
                    <h1>Hey, {session['username']}!</h1>
                    <p style="color: #666;">Welcome back to your overview.</p>
                </div>
                <div style="background: var(--surface); padding: 10px 20px; border-radius: 20px; border:1px solid #ddd; font-weight: bold;">
                    Rating: {hotel[7]}
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px;">
                <div style="background: var(--surface); padding: 24px; border-radius: 16px; border: 1px solid #eee;">
                    <p style="color:#666;">Total Rooms</p>
                    <h2>{hotel[4]}</h2>
                </div>
                <div style="background: var(--surface); padding: 24px; border-radius: 16px; border: 1px solid #eee;">
                    <p style="color:#666;">Total Staff</p>
                    <h2>{hotel[5]}</h2>
                </div>
                <div style="background: var(--surface); padding: 24px; border-radius: 16px; border: 1px solid #eee;">
                    <p style="color:#666;">Interns</p>
                    <h2>{hotel[6]}</h2>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
                <div style="background: var(--surface); padding: 24px; border-radius: 16px; border: 1px solid #eee;">
                    <h3 style="margin-bottom: 20px;">Live Booking List</h3>
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <tr style="border-bottom: 2px solid #f0f0f0; color: #666;">
                            <th style="padding: 12px 8px;">Booking ID</th>
                            <th style="padding: 12px 8px;">Guest</th>
                            <th style="padding: 12px 8px;">Status</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #f9f9f9;">
                            <td style="padding: 14px 8px; font-weight: bold;">#1024</td>
                            <td style="padding: 14px 8px;">Alice Wamae</td>
                            <td style="padding: 14px 8px; color: var(--dark); font-weight: bold;">Confirmed</td>
                        </tr>
                    </table>
                </div>
                <div style="background: var(--surface); padding: 24px; border-radius: 16px; border: 1px solid #eee;">
                    <h3 style="margin-bottom: 16px;">Features</h3>
                    {features_html}
                </div>
            </div>
        </div>
    '''

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
