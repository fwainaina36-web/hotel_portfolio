from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "francois_secret_key_2026"

def init_db():
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()

    # Create Tables Fresh
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS hotel(
        id INTEGER PRIMARY KEY, hotel_name TEXT, director TEXT, manager TEXT,
        total_rooms INTEGER, staff INTEGER, interns INTEGER
    )""")

    cursor.execute("DROP TABLE IF EXISTS rooms")
    cursor.execute("""CREATE TABLE rooms(
        room_number INTEGER PRIMARY KEY,
        room_type TEXT,
        status TEXT DEFAULT 'Available',
        price REAL,
        floor INTEGER,
        description TEXT
    )""")

    cursor.execute("DROP TABLE IF EXISTS bookings")
    cursor.execute("""CREATE TABLE bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT,
        room_number INTEGER,
        check_in TEXT,
        check_out TEXT,
        status TEXT DEFAULT 'Confirmed',
        amount REAL,
        phone TEXT,
        email TEXT,
        booking_date TEXT
    )""")

    # Insert Basic Data
    cursor.execute("INSERT OR IGNORE INTO users(username, password, role) VALUES(?, ?, ?)", 
                  ("Francis Mbugua", "FM@2026", "Director"))
    
    cursor.execute("INSERT OR IGNORE INTO hotel VALUES(1, 'Francois Grand Royal Resort & Spa', 'Francis Mbugua', 'Joseph Kamaru', 350, 200, 70)")

    # Seed Room allocation exactly to match client specifications
    cursor.execute("SELECT COUNT(*) FROM rooms")
    if cursor.fetchone()[0] == 0:
        rooms = []

        # Standard - 90 rooms
        for i in range(101, 191):
            rooms.append((i, "Standard", "Available", 18500, 1, "Standard Room"))

        # Deluxe - 55 rooms
        for i in range(201, 256):
            rooms.append((i, "Deluxe", "Available", 28500, 2, "Deluxe Room"))

        # Executive - 60 rooms
        for i in range(301, 361):
            rooms.append((i, "Executive", "Available", 42000, 3, "Executive Room"))

        # Presidential Suite - 5 rooms
        for i in range(401, 406):
            rooms.append((i, "Presidential Suite", "Available", 95000, 4, "Presidential Suite"))

        # Double - 70 rooms
        for i in range(501, 571):
            rooms.append((i, "Double", "Available", 22500, 5, "Double Room"))

        # Twin - 60 rooms
        for i in range(601, 661):
            rooms.append((i, "Twin", "Available", 23500, 6, "Twin Room"))

        # Junior Suite - 10 rooms
        for i in range(701, 711):
            rooms.append((i, "Junior Suite", "Available", 55000, 7, "Junior Suite"))

        cursor.executemany("INSERT INTO rooms VALUES(?,?,?,?,?,?)", rooms)

    conn.commit()
    conn.close()

init_db()

# ========================= BASE LAYOUT MACRO =========================
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - François Resort</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Poppins', sans-serif; }</style>
</head>
<body class="bg-slate-50 flex min-h-screen">

    <aside class="w-72 bg-slate-900 text-slate-200 flex flex-col justify-between fixed h-full z-10">
        <div class="p-6">
            <div class="flex items-center gap-3 mb-10">
                <div class="bg-emerald-500 text-white p-2 rounded-lg font-bold text-xl">🏨</div>
                <span class="text-2xl font-bold tracking-wide text-white">HOTEL</span>
            </div>
            <nav class="space-y-1">
                <a href="/dashboard" class="flex items-center gap-4 px-4 py-3 rounded-xl transition duration-200 {% if active == 'dashboard' %} bg-emerald-500 text-white font-medium {% else %} hover:bg-slate-800 text-slate-400 hover:text-white {% endif %}">
                    <span>📊</span> Dashboard
                </a>
                <a href="/bookings" class="flex items-center gap-4 px-4 py-3 rounded-xl transition duration-200 {% if active == 'bookings' %} bg-emerald-500 text-white font-medium {% else %} hover:bg-slate-800 text-slate-400 hover:text-white {% endif %}">
                    <span>📅</span> Booking
                </a>
                <a href="/rooms" class="flex items-center gap-4 px-4 py-3 rounded-xl transition duration-200 {% if active == 'rooms' %} bg-emerald-500 text-white font-medium {% else %} hover:bg-slate-800 text-slate-400 hover:text-white {% endif %}">
                    <span>🛏️</span> Rooms
                </a>
                <a href="#" class="flex items-center gap-4 px-4 py-3 rounded-xl text-slate-500 cursor-not-allowed">
                    <span>👥</span> Customers
                </a>
                <a href="#" class="flex items-center gap-4 px-4 py-3 rounded-xl text-slate-500 cursor-not-allowed">
                    <span>👔</span> Staff
                </a>
                <a href="#" class="flex items-center gap-4 px-4 py-3 rounded-xl text-slate-500 cursor-not-allowed">
                    <span>💰</span> Pricing
                </a>
            </nav>
        </div>
        <div class="p-6 border-t border-slate-800">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center font-bold text-white">FM</div>
                <div>
                    <p class="text-sm font-semibold text-white">Francis Mbugua</p>
                    <p class="text-xs text-slate-400">Director</p>
                </div>
            </div>
            <a href="/logout" class="block text-center bg-slate-800 hover:bg-rose-900/40 text-rose-400 hover:text-rose-300 py-2.5 rounded-xl text-sm font-medium transition">Logout</a>
        </div>
    </aside>

    <div class="flex-1 ml-72 flex flex-col">
        <header class="bg-white border-b border-slate-100 px-10 py-4 flex items-center justify-between sticky top-0 z-50">
            <div class="relative w-96">
                <input type="text" placeholder="Search here..." class="w-full bg-slate-100 text-sm pl-5 pr-10 py-2.5 rounded-full border border-transparent focus:outline-none focus:border-emerald-500 transition">
                <span class="absolute right-4 top-3 text-slate-400 text-sm">🔍</span>
            </div>
            <div class="flex items-center gap-6">
                <button class="relative text-slate-500 hover:text-emerald-500 text-xl">🔔<span class="absolute -top-1 -right-1 bg-emerald-500 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">3</span></button>
                <div class="w-[1px] h-6 bg-slate-200"></div>
                <span class="text-sm text-slate-600 font-medium">System Status: <span class="text-emerald-500 font-bold">Live</span></span>
            </div>
        </header>

        <main class="p-10 flex-1">
            {{ content | safe }}
        </main>
    </div>

</body>
</html>
"""

# ========================= ROUTES =========================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect("francois_resort.db")
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
    return """
    <!DOCTYPE html>
    <html><head><title>Login - François Resort</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    <style>body{font-family:'Poppins',sans-serif;}</style>
    </head>
    <body class="bg-gradient-to-br from-slate-900 to-slate-800 h-screen flex items-center justify-center p-4">
        <div class="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8 text-center">
            <h1 class="text-emerald-500 text-4xl font-bold tracking-tight mb-2">François Resort</h1>
            <p class="text-slate-500 text-sm mb-8">Luxury Hotel Management System Admin</p>
            <form method="POST" class="space-y-4">
                <input type="text" name="username" placeholder="Username" required class="w-full px-4 py-3.5 border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition">
                <input type="password" name="password" placeholder="Password" required class="w-full px-4 py-3.5 border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition">
                <button type="submit" class="w-full py-3.5 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-xl tracking-wide shadow-lg shadow-emerald-500/20 transition">Login to System</button>
            </form>
        </div>
    </body></html>
    """

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect(url_for("login"))
    
    conn = sqlite3.connect("francois_resort.db")
    total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    available_rooms = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'").fetchone()[0]
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    total_collections = conn.execute("SELECT IFNULL(SUM(amount), 0) FROM bookings").fetchone()[0]
    
    # Room Breakdown Data for Chart Allocation Ring
    breakdown = {}
    types = ["Standard", "Deluxe", "Executive", "Presidential Suite", "Double", "Twin", "Junior Suite"]
    for t in types:
        breakdown[t] = conn.execute("SELECT COUNT(*) FROM rooms WHERE room_type=?", (t,)).fetchone()[0]
    conn.close()

    dashboard_html = f"""
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800">Admin Dashboard</h1>
        <p class="text-slate-500 text-sm">Real-time breakdown overview of Francois Grand Royal Resort & Spa</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
            <div>
                <p class="text-2xl font-bold text-slate-800">{total_bookings}</p>
                <p class="text-sm font-medium text-slate-400 mt-1">Total Booking</p>
            </div>
            <div class="text-emerald-500 bg-emerald-50 p-3 rounded-xl text-xl">👥</div>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
            <div>
                <p class="text-2xl font-bold text-slate-800">{available_rooms}</p>
                <p class="text-sm font-medium text-slate-400 mt-1">Available Rooms</p>
            </div>
            <div class="text-cyan-500 bg-cyan-50 p-3 rounded-xl text-xl">🔑</div>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
            <div>
                <p class="text-2xl font-bold text-slate-800">1,538</p>
                <p class="text-sm font-medium text-slate-400 mt-1">Enquiry</p>
            </div>
            <div class="text-amber-500 bg-amber-50 p-3 rounded-xl text-xl">📝</div>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
            <div>
                <p class="text-2xl font-bold text-slate-800">KES {total_collections:,.0f}</p>
                <p class="text-sm font-medium text-slate-400 mt-1">Collections</p>
            </div>
            <div class="text-indigo-500 bg-indigo-50 p-3 rounded-xl text-xl">💵</div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm lg:col-span-2">
            <h3 class="text-lg font-bold text-slate-800 mb-4">VISITORS</h3>
            <div class="h-64">
                <canvas id="visitorsChart"></canvas>
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col items-center justify-center">
            <h3 class="text-lg font-bold text-slate-800 mb-4 self-start">ROOMS SUMMARY</h3>
            <div class="w-full max-w-[200px] relative flex items-center justify-center">
                <canvas id="roomsDoughnut"></canvas>
                <div class="absolute text-center">
                    <p class="text-2xl font-bold text-emerald-500">{total_rooms}</p>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Rooms</p>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-x-6 gap-y-2 mt-6 w-full text-xs text-slate-600 border-t pt-4">
                <div>🟨 Standard: <b>{breakdown['Standard']}</b></div>
                <div>🟩 Deluxe: <b>{breakdown['Deluxe']}</b></div>
                <div>🟦 Exec: <b>{breakdown['Executive']}</b></div>
                <div>🟪 Junior: <b>{breakdown['Junior Suite']}</b></div>
                <div>🟥 Pres: <b>{breakdown['Presidential Suite']}</b></div>
                <div>🟧 Others: <b>{breakdown['Double'] + breakdown['Twin']}</b></div>
            </div>
        </div>
    </div>

    <script>
        // Visitors Line Chart
        const ctxLine = document.getElementById('visitorsChart').getContext('2d');
        new Chart(ctxLine, {{
            type: 'line',
            data: {{
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{{
                    label: 'Visitor Traffic Index',
                    data: [65, 45, 75, 50, 85, 60, 95],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.05)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});

        // Rooms Breakdown Doughnut Ring
        const ctxRing = document.getElementById('roomsDoughnut').getContext('2d');
        new Chart(ctxRing, {{
            type: 'doughnut',
            data: {{
                labels: ['Standard', 'Deluxe', 'Executive', 'Presidential', 'Double', 'Twin', 'Junior'],
                datasets: [{{
                    data: [{breakdown['Standard']}, {breakdown['Deluxe']}, {breakdown['Executive']}, {breakdown['Presidential Suite']}, {breakdown['Double']}, {breakdown['Twin']}, {breakdown['Junior Suite']}],
                    backgroundColor: ['#f59e0b', '#10b981', '#3b82f6', '#ec4899', '#f97316', '#6366f1', '#a855f7'],
                    borderWidth: 2
                }}]
            }},
            options: {{ cutout: '75%', responsive: true, plugins: {{ legend: {{ display: false }} }} }}
        }});
    </script>
    """
    return render_template_string(BASE_LAYOUT, title="Dashboard", active="dashboard", content=dashboard_html)

@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    if "user" not in session: return redirect(url_for("login"))

    conn = sqlite3.connect("francois_resort.db")
    if request.method == "POST":
        room_number = int(request.form["room_number"])
        new_status = request.form.get("status")
        new_price = request.form.get("new_price")

        if new_price:
            conn.execute("UPDATE rooms SET price = ? WHERE room_number = ?", (float(new_price), room_number))
        if new_status:
            conn.execute("UPDATE rooms SET status = ? WHERE room_number = ?", (new_status, room_number))
        conn.commit()
        conn.close()
        return redirect(url_for("rooms"))

    rooms_list = conn.execute("SELECT * FROM rooms ORDER BY room_number").fetchall()
    conn.close()

    rooms_html = """
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800">Room Management</h1>
        <p class="text-slate-500 text-sm">Live status updates across your 350 rooms</p>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-fit">
            <h3 class="text-lg font-bold text-slate-800 mb-4">Quick Update Panel</h3>
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Select Room Target</label>
                    <select name="room_number" required class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition">
                        <option value="">-- Choose Room --</option>
                        {% for r in rooms_list %}
                        <option value="{{ r[0] }}">Room {{ r[0] }} ({{ r[1] }})</option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Operational Status</label>
                    <select name="status" class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition">
                        <option value="Available">Available</option>
                        <option value="Occupied">Occupied</option>
                        <option value="Cleaning">Cleaning</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Override Price (KES)</label>
                    <input type="number" name="new_price" placeholder="Optional adjustment value" class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition">
                </div>
                <button type="submit" class="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-xl tracking-wide shadow-md transition">Apply Management Changes</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm xl:col-span-2">
            <h3 class="text-lg font-bold text-slate-800 mb-4">Complete Live Room Registry</h3>
            <div class="overflow-x-auto max-h-[600px] overflow-y-auto border border-slate-100 rounded-xl">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-slate-400 text-xs uppercase tracking-wider font-semibold border-b border-slate-100">
                            <th class="p-4">Room No</th>
                            <th class="p-4">Type Class</th>
                            <th class="p-4">Floor Map</th>
                            <th class="p-4">Base Rate</th>
                            <th class="p-4">Status</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-slate-600 divide-y divide-slate-50">
                        {% for r in rooms_list %}
                        <tr class="hover:bg-slate-50/80 transition">
                            <td class="p-4 font-bold text-slate-800">#{{ r[0] }}</td>
                            <td class="p-4"><span class="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700">{{ r[1] }}</span></td>
                            <td class="p-4 text-slate-500">Floor Level {{ r[4] }}</td>
                            <td class="p-4 font-semibold text-slate-700">KES {{ "{:,.2f}".format(r[3]) }}</td>
                            <td class="p-4">
                                {% if r[2] == 'Available' %}
                                <span class="text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full text-xs font-semibold">Available</span>
                                {% elif r[2] == 'Occupied' %}
                                <span class="text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full text-xs font-semibold">Occupied</span>
                                {% else %}
                                <span class="text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full text-xs font-semibold">Cleaning</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, title="Rooms", active="rooms", content=render_template_string(rooms_html, rooms_list=rooms_list))

@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    if "user" not in session: return redirect(url_for("login"))
    
    conn = sqlite3.connect("francois_resort.db")
    if request.method == "POST":
        guest = request.form["guest"]
        room = int(request.form["room"])
        checkin = request.form["checkin"]
        checkout = request.form["checkout"]
        amount = float(request.form["amount"])
        phone = request.form["phone"]
        email = request.form.get("email", "")
        
        conn.execute("""INSERT INTO bookings(guest_name, room_number, check_in, check_out, amount, phone, email, booking_date)
                     VALUES(?,?,?,?,?,?,?,?)""", (guest, room, checkin, checkout, amount, phone, email, date.today().isoformat()))
        conn.execute("UPDATE rooms SET status = 'Occupied' WHERE room_number = ?", (room,))
        conn.commit()
        conn.close()
        return redirect(url_for("bookings"))

    available_selection = conn.execute("SELECT room_number, room_type, price FROM rooms WHERE status='Available'").fetchall()
    history_logs = conn.execute("SELECT id, guest_name, room_number, check_in, check_out, amount, phone FROM bookings ORDER BY id DESC").fetchall()
    conn.close()

    bookings_html = """
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800">Booking Processing Engine</h1>
        <p class="text-slate-500 text-sm">Register upcoming checking arrivals or review structural rental histories.</p>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-fit">
            <h3 class="text-lg font-bold text-slate-800 mb-4">New Reservation Entry</h3>
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Guest Full Name</label>
                    <input type="text" name="guest" required placeholder="John Doe" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Contact Phone Number</label>
                    <input type="text" name="phone" required placeholder="+254..." class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Email Address</label>
                    <input type="email" name="email" placeholder="john@example.com" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Assign Free Room Unit</label>
                    <select name="room" required id="room_select" onchange="updatePrice()" class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                        <option value="">-- Select Available Room --</option>
                        {% for rm in available_selection %}
                        <option value="{{ rm[0] }}" data-price="{{ rm[2] }}">Room {{ rm[0] }} - {{ rm[1] }} (KES {{ rm[2] }})</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Check-in</label>
                        <input type="date" name="checkin" required class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Check-out</label>
                        <input type="date" name="checkout" required class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Total Payment Amount (KES)</label>
                    <input type="number" step="0.01" name="amount" id="amount_input" required class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-100 text-sm font-bold text-slate-800 focus:outline-none">
                </div>
                <button type="submit" class="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-xl tracking-wide shadow-md transition">Confirm Live Booking</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm xl:col-span-2">
            <h3 class="text-lg font-bold text-slate-800 mb-4">Recent Booked Manifest Logs</h3>
            <div class="overflow-x-auto max-h-[600px] overflow-y-auto border border-slate-100 rounded-xl">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-slate-400 text-xs uppercase tracking-wider font-semibold border-b border-slate-100">
                            <th class="p-4">ID</th>
                            <th class="p-4">Guest Name</th>
                            <th class="p-4">Room No</th>
                            <th class="p-4">Timeline Dates</th>
                            <th class="p-4">Paid Total</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-slate-600 divide-y divide-slate-50">
                        {% for bk in history_logs %}
                        <tr class="hover:bg-slate-50/80 transition">
                            <td class="p-4 text-slate-400">#{{ bk[0] }}</td>
                            <td class="p-4 font-bold text-slate-800">{{ bk[1] }}<br><span class="text-xs font-normal text-slate-400">{{ bk[6] }}</span></td>
                            <td class="p-4"><span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-medium text-xs">Room {{ bk[2] }}</span></td>
                            <td class="p-4 text-xs text-slate-500">In: <b>{{ bk[3] }}</b><br>Out: <b>{{ bk[4] }}</b></td>
                            <td class="p-4 font-bold text-emerald-600">KES {{ "{:,.2f}".format(bk[5]) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function updatePrice() {
            var select = document.getElementById('room_select');
            var selectedOption = select.options[select.selectedIndex];
            var price = selectedOption.getAttribute('data-price');
            if(price) {
                document.getElementById('amount_input').value = price;
            } else {
                document.getElementById('amount_input').value = '';
            }
        }
    </script>
    """
    return render_template_string(BASE_LAYOUT, title="Bookings", active="bookings", content=render_template_string(bookings_html, available_selection=available_selection, history_logs=history_logs))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)