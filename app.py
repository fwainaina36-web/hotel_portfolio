from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "francois_secret_key_2026"

def init_db():
    conn = sqlite3.connect("francois_resort.db")
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY, 
        username TEXT UNIQUE, 
        password TEXT, 
        role TEXT
    )""")

    # 2. Hotel Table
    cursor.execute("""CREATE TABLE IF NOT EXISTS hotel(
        id INTEGER PRIMARY KEY, 
        hotel_name TEXT, 
        director TEXT, 
        manager TEXT,
        total_rooms INTEGER, 
        staff INTEGER, 
        interns INTEGER
    )""")

    # 3. Rooms Table
    cursor.execute("""CREATE TABLE IF NOT EXISTS rooms(
        room_number INTEGER PRIMARY KEY,
        room_type TEXT,
        status TEXT DEFAULT 'Available',
        price REAL,
        floor INTEGER,
        description TEXT
    )""")

    # 4. Bookings Table
    cursor.execute("""CREATE TABLE IF NOT EXISTS bookings(
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

    # 5. Staff Members Table
    cursor.execute("""CREATE TABLE IF NOT EXISTS staff_members(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        salary REAL,
        phone TEXT
    )""")

    # 6. Pricing Rates Table
    cursor.execute("""CREATE TABLE IF NOT EXISTS pricing_rates(
        room_type TEXT PRIMARY KEY,
        base_rate REAL
    )""")

    # Seed Admin User
    cursor.execute("INSERT OR IGNORE INTO users(username, password, role) VALUES(?, ?, ?)", 
                  ("Francis Mbugua", "FM@2026", "Director"))
    
    # Seed Hotel Information
    cursor.execute("INSERT OR IGNORE INTO hotel VALUES(1, 'Francois Grand Royal Resort & Spa', 'Francis Mbugua', 'Joseph Kamaru', 350, 200, 70)")

    # Seed Room Allocations (350 rooms total)
    cursor.execute("SELECT COUNT(*) FROM rooms")
    if cursor.fetchone()[0] == 0:
        rooms = []
        for i in range(101, 191): rooms.append((i, "Standard", "Available", 18500, 1, "Standard Room"))
        for i in range(201, 256): rooms.append((i, "Deluxe", "Available", 28500, 2, "Deluxe Room"))
        for i in range(301, 361): rooms.append((i, "Executive", "Available", 42000, 3, "Executive Room"))
        for i in range(401, 406): rooms.append((i, "Presidential Suite", "Available", 95000, 4, "Presidential Suite"))
        for i in range(501, 571): rooms.append((i, "Double", "Available", 22500, 5, "Double Room"))
        for i in range(601, 661): rooms.append((i, "Twin", "Available", 23500, 6, "Twin Room"))
        for i in range(701, 711): rooms.append((i, "Junior Suite", "Available", 55000, 7, "Junior Suite"))
        cursor.executemany("INSERT INTO rooms VALUES(?,?,?,?,?,?)", rooms)

    # Seed Baseline Pricing Structures
    rates = [("Standard", 18500), ("Deluxe", 28500), ("Executive", 42000), 
             ("Presidential Suite", 95000), ("Double", 22500), ("Twin", 23500), ("Junior Suite", 55000)]
    cursor.executemany("INSERT OR IGNORE INTO pricing_rates VALUES(?,?)", rates)

    # Seed Default Dummy Staff Details
    cursor.execute("SELECT COUNT(*) FROM staff_members")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO staff_members (name, role, salary, phone) VALUES (?, ?, ?, ?)", ("Alice Wanjiku", "Receptionist", 45000, "+254711223344"))
        cursor.execute("INSERT INTO staff_members (name, role, salary, phone) VALUES (?, ?, ?, ?)", ("John Mwangi", "Chef", 65000, "+254722334455"))

    conn.commit()
    conn.close()

init_db()

# ========================= BASE LAYOUT TEMPLATE =========================
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

    <!-- Sidebar Navigation -->
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
                <a href="/customers" class="flex items-center gap-4 px-4 py-3 rounded-xl transition duration-200 {% if active == 'customers' %} bg-emerald-500 text-white font-medium {% else %} hover:bg-slate-800 text-slate-400 hover:text-white {% endif %}">
                    <span>👥</span> Customers
                </a>
                <a href="/staff" class="flex items-center gap-4 px-4 py-3 rounded-xl transition duration-200 {% if active == 'staff' %} bg-emerald-500 text-white font-medium {% else %} hover:bg-slate-800 text-slate-400 hover:text-white {% endif %}">
                    <span>👔</span> Staff
                </a>
                <a href="/pricing" class="flex items-center gap-4 px-4 py-3 rounded-xl transition duration-200 {% if active == 'pricing' %} bg-emerald-500 text-white font-medium {% else %} hover:bg-slate-800 text-slate-400 hover:text-white {% endif %}">
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

    <!-- Main Workspace Container -->
    <div class="flex-1 ml-72 flex flex-col">
        <!-- Top Sticky Header -->
        <header class="bg-white border-b border-slate-100 px-10 py-4 flex items-center justify-between sticky top-0 z-50">
            <div class="relative w-96">
                <input type="text" placeholder="Search here..." class="w-full bg-slate-100 text-sm pl-5 pr-10 py-2.5 rounded-full border border-transparent focus:outline-none focus:border-emerald-500 transition">
                <span class="absolute right-4 top-3 text-slate-400 text-sm">🔍</span>
            </div>
            <div class="flex items-center gap-6">
                <button class="relative text-slate-500 hover:text-emerald-500 text-xl">
                    🔔<span class="absolute -top-1 -right-1 bg-emerald-500 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">3</span>
                </button>
                <div class="w-[1px] h-6 bg-slate-200"></div>
                <span class="text-sm text-slate-600 font-medium">System Status: <span class="text-emerald-500 font-bold">Live</span></span>
            </div>
        </header>

        <!-- Main Body Workspace Injection View -->
        <main class="p-10 flex-1">
            {{ content | safe }}
        </main>
    </div>

</body>
</html>
"""

# ========================= APPLICATION CONTROLLER ROUTES =========================

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
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    total_collections = conn.execute("SELECT IFNULL(SUM(amount), 0) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    
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
            <div><p class="text-2xl font-bold text-slate-800">{{total_bookings}}</p><p class="text-sm font-medium text-slate-400 mt-1">Active Bookings</p></div>
            <div class="text-emerald-500 bg-emerald-50 p-3 rounded-xl text-xl">👥</div>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
            <div><p class="text-2xl font-bold text-slate-800">{{available_rooms}}</p><p class="text-sm font-medium text-slate-400 mt-1">Available Rooms</p></div>
            <div class="text-cyan-500 bg-cyan-50 p-3 rounded-xl text-xl">🔑</div>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
            <div><p class="text-2xl font-bold text-slate-800">1,538</p><p class="text-sm font-medium text-slate-400 mt-1">Enquiry</p></div>
            <div class="text-amber-500 bg-amber-50 p-3 rounded-xl text-xl">📝</div>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
            <div><p class="text-2xl font-bold text-slate-800">KES {total_collections:,.0f}</p><p class="text-sm font-medium text-slate-400 mt-1">Collections</p></div>
            <div class="text-indigo-500 bg-indigo-50 p-3 rounded-xl text-xl">💵</div>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm lg:col-span-2">
            <h3 class="text-lg font-bold text-slate-800 mb-4">VISITORS</h3>
            <div class="h-64"><canvas id="visitorsChart"></canvas></div>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col items-center justify-center">
            <h3 class="text-lg font-bold text-slate-800 mb-4 self-start">ROOMS SUMMARY</h3>
            <div class="w-full max-w-[200px] relative flex items-center justify-center">
                <canvas id="roomsDoughnut"></canvas>
                <div class="absolute text-center">
                    <p class="text-2xl font-bold text-emerald-500">{{total_rooms}}</p>
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
                    borderWidth: 3, tension: 0.4, fill: true
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});

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
    return render_template_string(BASE_LAYOUT, title="Dashboard", active="dashboard", content=render_template_string(dashboard_html, total_bookings=total_bookings, available_rooms=available_rooms, total_rooms=total_rooms))

@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    if "user" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("francois_resort.db")
    if request.method == "POST":
        room_number = int(request.form["room_number"])
        new_status = request.form.get("status")
        new_price = request.form.get("new_price")
        if new_price: conn.execute("UPDATE rooms SET price = ? WHERE room_number = ?", (float(new_price), room_number))
        if new_status: conn.execute("UPDATE rooms SET status = ? WHERE room_number = ?", (new_status, room_number))
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
                    <select name="room_number" required class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none">
                        {% for r in rooms_list %}<option value="{{ r[0] }}">Room {{ r[0] }} ({{ r[1] }})</option>{% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Status</label>
                    <select name="status" class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none">
                        <option value="Available">Available</option>
                        <option value="Occupied">Occupied</option>
                        <option value="Cleaning">Cleaning</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Override Price (KES)</label>
                    <input type="number" name="new_price" class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none">
                </div>
                <button type="submit" class="w-full py-3 bg-emerald-500 text-white font-semibold rounded-xl">Apply Changes</button>
            </form>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm xl:col-span-2">
            <div class="overflow-x-auto max-h-[500px] border rounded-xl">
                <table class="w-full text-left">
                    <tr class="bg-slate-50 text-xs text-slate-400 uppercase border-b">
                        <th class="p-4">Room No</th><th class="p-4">Type</th><th class="p-4">Floor</th><th class="p-4">Base Rate</th><th class="p-4">Status</th>
                    </tr>
                    {% for r in rooms_list %}
                    <tr class="text-sm border-b hover:bg-slate-50">
                        <td class="p-4 font-bold text-slate-800">#{{ r[0] }}</td><td class="p-4">{{ r[1] }}</td><td class="p-4">Level {{ r[4] }}</td><td class="p-4 font-semibold">KES {{ "{:,.2f}".format(r[3]) }}</td>
                        <td class="p-4"><span class="px-2 py-1 rounded-full text-xs font-semibold {% if r[2]=='Available' %} bg-emerald-50 text-emerald-600 {% else %} bg-amber-50 text-amber-600 {% endif %}">{{ r[2] }}</span></td>
                    </tr>
                    {% endfor %}
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
        action = request.form.get("action_type", "create")
        
        if action == "cancel_booking":
            booking_id = int(request.form["booking_id"])
            # Get room number linked to booking to free it back up
            target_booking = conn.execute("SELECT room_number FROM bookings WHERE id = ?", (booking_id,)).fetchone()
            if target_booking:
                room_no = target_booking[0]
                conn.execute("UPDATE rooms SET status = 'Available' WHERE room_number = ?", (room_no,))
            # Remove booking registry cleanly
            conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
            conn.commit()
            
        else:
            guest = request.form["guest"]
            room = int(request.form["room"])
            checkin = request.form["checkin"]
            checkout = request.form["checkout"]
            amount = float(request.form["amount"])
            phone = request.form["phone"]
            email = request.form.get("email", "")
            
            conn.execute("INSERT INTO bookings(guest_name, room_number, check_in, check_out, amount, phone, email, booking_date) VALUES(?,?,?,?,?,?,?,?)", 
                         (guest, room, checkin, checkout, amount, phone, email, date.today().isoformat()))
            conn.execute("UPDATE rooms SET status = 'Occupied' WHERE room_number = ?", (room,))
            conn.commit()
            
        conn.close()
        return redirect(url_for("bookings"))
        
    available_selection = conn.execute("SELECT room_number, room_type, price FROM rooms WHERE status='Available'").fetchall()
    history_logs = conn.execute("SELECT id, guest_name, room_number, check_in, check_out, amount, phone FROM bookings ORDER BY id DESC").fetchall()
    conn.close()

    bookings_html = """
    <div class="mb-8"><h1 class="text-3xl font-bold text-slate-800">Booking Processing Engine</h1></div>
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div class="space-y-6">
            <!-- Form 1: Reserve Booking Slot -->
            <div class="bg-white p-6 rounded-2xl border shadow-sm h-fit">
                <h3 class="text-md font-bold text-slate-700 mb-3">Process Reservation</h3>
                <form method="POST" class="space-y-4">
                    <input type="hidden" name="action_type" value="create">
                    <input type="text" name="guest" placeholder="Guest Full Name" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    <input type="text" name="phone" placeholder="Phone Number" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    <input type="email" name="email" placeholder="Email Address" class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    <select name="room" required id="room_select" onchange="updatePrice()" class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                        <option value="">-- Select Available Room --</option>
                        {% for rm in available_selection %}<option value="{{ rm[0] }}" data-price="{{ rm[2] }}">Room {{ rm[0] }} - {{ rm[1] }}</option>{% endfor %}
                    </select>
                    <div class="grid grid-cols-2 gap-4">
                        <input type="date" name="checkin" id="checkin" onchange="calculateAutoPrice()" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                        <input type="date" name="checkout" id="checkout" onchange="calculateAutoPrice()" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">Total Stay Cost (Editable Manually)</label>
                        <input type="number" step="0.01" name="amount" id="amount_input" placeholder="Total Amount (KES)" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500">
                    </div>
                    <button type="submit" class="w-full py-3 bg-emerald-500 text-white font-semibold rounded-xl">Confirm Booking</button>
                </form>
            </div>
            
            <!-- Form 2: Quick Remove/Cancel Slot -->
            <div class="bg-white p-6 rounded-2xl border border-rose-100 shadow-sm h-fit">
                <h3 class="text-md font-bold text-rose-800 mb-3">Cancel Active Booking Slot</h3>
                <form method="POST" onsubmit="return confirm('Release room allocation and remove booking record?');" class="space-y-4">
                    <input type="hidden" name="action_type" value="cancel_booking">
                    <select name="booking_id" required class="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none">
                        <option value="">-- Choose Active Schedule --</option>
                        {% for bk in history_logs %}
                        <option value="{{ bk[0] }}">{{ bk[1] }} (Room {{ bk[2] }})</option>
                        {% endfor %}
                    </select>
                    <button type="submit" class="w-full py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-medium text-sm rounded-xl transition">Revoke Booking</button>
                </form>
            </div>
        </div>
        
        <!-- Table Log History Output Display Summary Workspace -->
        <div class="bg-white p-6 rounded-2xl border shadow-sm xl:col-span-2">
            <div class="overflow-x-auto max-h-[580px] border rounded-xl">
                <table class="w-full text-left">
                    <tr class="bg-slate-50 text-xs text-slate-400 border-b"><th class="p-4">Guest</th><th class="p-4">Room</th><th class="p-4">Timeline</th><th class="p-4">Paid Total</th><th class="p-4 text-center">Action</th></tr>
                    {% for bk in history_logs %}
                    <tr class="text-sm border-b hover:bg-slate-50">
                        <td class="p-4 font-bold">{{ bk[1] }}<br><span class="text-xs font-normal text-slate-400">{{ bk[6] }}</span></td>
                        <td class="p-4"><span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded text-xs">Room {{ bk[2] }}</span></td>
                        <td class="p-4 text-xs">In: {{ bk[3] }}<br>Out: {{ bk[4] }}</td>
                        <td class="p-4 font-bold text-emerald-600">KES {{ "{:,.2f}".format(bk[5]) }}</td>
                        <td class="p-4 text-center">
                            <form method="POST" onsubmit="return confirm('Cancel reservation for {{ bk[1] }}?');" class="inline">
                                <input type="hidden" name="action_type" value="cancel_booking">
                                <input type="hidden" name="booking_id" value="{{ bk[0] }}">
                                <button type="submit" class="text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 transition">Cancel</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
    <script>
        function updatePrice() {
            calculateAutoPrice();
        }
        
        function calculateAutoPrice() {
            var select = document.getElementById('room_select');
            var selectedOption = select.options[select.selectedIndex];
            var basePrice = selectedOption.getAttribute('data-price');
            
            if (!basePrice) {
                document.getElementById('amount_input').value = '';
                return;
            }
            
            var checkinVal = document.getElementById('checkin').value;
            var checkoutVal = document.getElementById('checkout').value;
            
            if (checkinVal && checkoutVal) {
                var d1 = new Date(checkinVal);
                var d2 = new Date(checkoutVal);
                var timeDiff = d2.getTime() - d1.getTime();
                var days = Math.ceil(timeDiff / (1000 * 3600 * 24));
                
                if (days > 0) {
                    // Automatically adjusts calculation based on duration (e.g., 8 days for a week and a day)
                    document.getElementById('amount_input').value = (parseFloat(basePrice) * days).toFixed(2);
                } else {
                    document.getElementById('amount_input').value = parseFloat(basePrice).toFixed(2);
                }
            } else {
                document.getElementById('amount_input').value = parseFloat(basePrice).toFixed(2);
            }
        }
    </script>
    """
    return render_template_string(BASE_LAYOUT, title="Bookings", active="bookings", content=render_template_string(bookings_html, available_selection=available_selection, history_logs=history_logs))


# ========================= UNLOCKED DIRECTORY WORKSPACES =========================

@app.route("/customers")
def customers():
    if "user" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("francois_resort.db")
    customer_logs = conn.execute("SELECT DISTINCT guest_name, phone, email, booking_date FROM bookings ORDER BY booking_date DESC").fetchall()
    conn.close()

    customers_html = """
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800">Customer Directory</h1>
        <p class="text-slate-500 text-sm">Dynamic view of registered guests derived from current and historic stays.</p>
    </div>
    <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
        <div class="overflow-x-auto rounded-xl border border-slate-100">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-slate-50 text-slate-400 text-xs uppercase font-semibold border-b">
                        <th class="p-4">Customer Name</th><th class="p-4">Contact Phone</th><th class="p-4">Email Address</th><th class="p-4">Last Activity Date</th>
                    </tr>
                </thead>
                <tbody class="text-sm text-slate-600 divide-y">
                    {% if not customer_logs %}
                    <tr><td colspan="4" class="p-8 text-center text-slate-400">No active guest logs found in system database. Check-in a room to seed data!</td></tr>
                    {% endif %}
                    {% for c in customer_logs %}
                    <tr class="hover:bg-slate-50/80 transition">
                        <td class="p-4 font-bold text-slate-800">{{ c[0] }}</td>
                        <td class="p-4 text-slate-600">{{ c[1] }}</td>
                        <td class="p-4 text-slate-500">{{ c[2] if c[2] else 'N/A' }}</td>
                        <td class="p-4 font-medium text-emerald-600">{{ c[3] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, title="Customers", active="customers", content=render_template_string(customers_html, customer_logs=customer_logs))

@app.route("/staff", methods=["GET", "POST"])
def staff():
    if "user" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("francois_resort.db")
    
    if request.method == "POST":
        action = request.form.get("action_type")
        
        if action == "remove_staff":
            staff_id = int(request.form["staff_id"])
            conn.execute("DELETE FROM staff_members WHERE id = ?", (staff_id,))
            conn.commit()

        elif action == "adjust_salary":
            staff_id = int(request.form["staff_id"])
            new_salary = float(request.form["new_salary"])
            conn.execute("UPDATE staff_members SET salary = ? WHERE id = ?", (new_salary, staff_id))
            conn.commit()
        
        else:
            name = request.form["name"]
            role = request.form["role"]
            salary = float(request.form["salary"])
            phone = request.form["phone"]
            conn.execute("INSERT INTO staff_members(name, role, salary, phone) VALUES(?,?,?,?)", (name, role, salary, phone))
            conn.commit()
            
        return redirect(url_for("staff"))
    
    staff_list = conn.execute("SELECT * FROM staff_members").fetchall()
    conn.close()

    staff_html = """
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800">Staff & Employee Management</h1>
        <p class="text-slate-500 text-sm">Register internal hotel staff roles, salary index sheets, and contacts.</p>
    </div>
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div class="space-y-6">
            <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-fit">
                <h3 class="text-lg font-bold text-slate-800 mb-4">Onboard New Employee</h3>
                <form method="POST" class="space-y-4">
                    <input type="hidden" name="action_type" value="onboard">
                    <input type="text" name="name" placeholder="Full Name" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    <input type="text" name="role" placeholder="Role (e.g. Concierge, Accountant)" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    <input type="number" name="salary" placeholder="Monthly Salary (KES)" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    <input type="text" name="phone" placeholder="Phone Contact" required class="w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                    <button type="submit" class="w-full py-3 bg-emerald-500 text-white font-semibold rounded-xl">Register Staff Member</button>
                </form>
            </div>

            <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-fit">
                <h3 class="text-lg font-bold text-slate-800 mb-4">Restructure Staff Salary</h3>
                <form method="POST" class="space-y-4">
                    <input type="hidden" name="action_type" value="adjust_salary">
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Select Onboarded Employee</label>
                        <select name="staff_id" required class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none">
                            {% for s in staff_list %}<option value="{{ s[0] }}">{{ s[1] }} ({{ s[2] }})</option>{% endfor %}
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">New Restructured Salary (KES)</label>
                        <input type="number" step="0.01" name="new_salary" placeholder="Enter updated wage index" required class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none">
                    </div>
                    <button type="submit" class="w-full py-3 bg-amber-500 text-white font-semibold rounded-xl transition duration-150 hover:bg-amber-600">Update Salary Structure</button>
                </form>
            </div>

            <div class="bg-white p-6 rounded-2xl border border-rose-100 shadow-sm h-fit">
                <h3 class="text-lg font-bold text-rose-800 mb-4">Remove Staff Member</h3>
                <form method="POST" onsubmit="return confirm('Are you sure you want to completely offboard this staff member?');" class="space-y-4">
                    <input type="hidden" name="action_type" value="remove_staff">
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Select Staff Target</label>
                        <select name="staff_id" required class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none">
                            {% for s in staff_list %}<option value="{{ s[0] }}">{{ s[1] }} [ID: #{{ s[0] }}]</option>{% endfor %}
                        </select>
                    </div>
                    <button type="submit" class="w-full py-3 bg-rose-600 text-white font-semibold rounded-xl transition duration-150 hover:bg-rose-700 shadow-md shadow-rose-200">Terminate Profile</button>
                </form>
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm xl:col-span-2">
            <div class="overflow-x-auto rounded-xl border">
                <table class="w-full text-left">
                    <tr class="bg-slate-50 text-xs text-slate-400 border-b"><th class="p-4">ID</th><th class="p-4">Name</th><th class="p-4">Role Designation</th><th class="p-4">Salary Base</th><th class="p-4 text-center">Action</th></tr>
                    {% for s in staff_list %}
                    <tr class="text-sm border-b hover:bg-slate-50">
                        <td class="p-4 text-slate-400">#{{ s[0] }}</td>
                        <td class="p-4 font-bold text-slate-800">{{ s[1] }}<br><span class="text-xs font-normal text-slate-400">{{ s[4] }}</span></td>
                        <td class="p-4"><span class="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md text-xs font-medium">{{ s[2] }}</span></td>
                        <td class="p-4 font-semibold text-emerald-600">KES {{ "{:,.2f}".format(s[3]) }}</td>
                        <td class="p-4 text-center">
                            <form method="POST" onsubmit="return confirm('Permanently delete {{ s[1] }} from system directory?');" class="inline">
                                <input type="hidden" name="action_type" value="remove_staff">
                                <input type="hidden" name="staff_id" value="{{ s[0] }}">
                                <button type="submit" class="text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 transition">Delete</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, title="Staff", active="staff", content=render_template_string(staff_html, staff_list=staff_list))

@app.route("/pricing", methods=["GET", "POST"])
def pricing():
    if "user" not in session: return redirect(url_for("login"))
    conn = sqlite3.connect("francois_resort.db")
    if request.method == "POST":
        room_type = request.form["room_type"]
        new_rate = float(request.form["rate"])
        conn.execute("UPDATE pricing_rates SET base_rate = ? WHERE room_type = ?", (new_rate, room_type))
        conn.execute("UPDATE rooms SET price = ? WHERE room_type = ? AND status='Available'", (new_rate, room_type))
        conn.commit()
        return redirect(url_for("pricing"))
    
    pricing_list = conn.execute("SELECT * FROM pricing_rates").fetchall()
    conn.close()

    pricing_html = """
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-800">Global Pricing Strategy Matrix</h1>
        <p class="text-slate-500 text-sm">Batch modify baseline room rates. Updates will auto-apply instantly across all available inventory matches.</p>
    </div>
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-fit">
            <h3 class="text-lg font-bold text-slate-800 mb-4">Update Tier Category Rate</h3>
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">Room Type Tier</label>
                    <select name="room_type" required class="w-full px-4 py-3 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                        {% for p in pricing_list %}<option value="{{ p[0] }}">{{ p[0] }}</option>{% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase mb-2">New Core Rate (KES)</label>
                    <input type="number" name="rate" placeholder="e.g. 20000" required class="w-full px-4 py-3 border rounded-xl bg-slate-50 text-sm focus:outline-none">
                </div>
                <button type="submit" class="w-full py-3 bg-emerald-500 text-white font-semibold rounded-xl">Broadcast Global Rate Alteration</button>
            </form>
        </div>
        <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm xl:col-span-2">
            <div class="overflow-x-auto rounded-xl border">
                <table class="w-full text-left">
                    <tr class="bg-slate-50 text-xs text-slate-400 border-b"><th class="p-4">Room Structural Tier Class</th><th class="p-4">Configured Active Base Rate</th></tr>
                    {% for p in pricing_list %}
                    <tr class="text-sm border-b hover:bg-slate-50">
                        <td class="p-4 font-bold text-slate-800">{{ p[0] }}</td>
                        <td class="p-4 font-bold text-emerald-600">KES {{ "{:,.2f}".format(p[1]) }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, title="Pricing", active="pricing", content=render_template_string(pricing_html, pricing_list=pricing_list))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)