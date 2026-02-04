from flask import Flask, render_template, request, send_file, redirect, url_for, session
import mysql.connector
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = 'nairobi_vibes_2026'

# --- 1. REMOTE DATABASE CONFIG (For FreeSQLDatabase) ---
# Replace these values with the exact ones emailed to you by FreeSQLDatabase
DB_CONFIG = {
    'host': 'sqlX.freesqldatabase.com', # Change 'X' to your assigned server number
    'user': 'your_db_user',
    'password': 'your_db_password',
    'database': 'your_db_name',
    'port': 3306,
    'ssl_disabled': True 
}


if not os.path.exists('tickets'):
    os.makedirs('tickets')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    gender = request.form.get('gender')
    v_type = request.form.get('vehicle_type')
    route = request.form.get('bus_type')
    seat = request.form.get('seat')
    mpesa = request.form.get('mpesa_id').upper()
    travel_time = request.form.get('travel_time')
    
    booking_date = datetime.now().strftime("%d-%b-%Y %H:%M")


    def calculate_price(route_str, vehicle):
        base = 80
        r_low = route_str.lower()
        if any(w in r_low for w in ["ngong", "rongai", "kiserian", "kitengela"]): base = 120
        elif any(w in r_low for w in ["westlands", "upperhill"]): base = 50
        elif any(w in r_low for w in ["thika", "ruiru", "limuru"]): base = 150
        if vehicle == "Nganya": base += 50
        return base

    final_fare = calculate_price(route, v_type)

    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        time_details = f"Travel: {travel_time} | Booked: {booking_date} | Sex: {gender} | Ref: {mpesa} | Fare: {final_fare}"
        
        cursor.execute(
            "INSERT INTO tickets (customer_name, bus_type, seat_number, travel_time) VALUES (%s, %s, %s, %s)",
            (name, f"{v_type}: {route}", seat, time_details)
        )
        conn.commit()
        ticket_id = cursor.lastrowid
        
    
        pdf_path = f"tickets/Ticket_{ticket_id}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setStrokeColor(colors.black); c.rect(50, 580, 500, 220, stroke=1)
        c.setFont("Helvetica-Bold", 18); c.drawString(70, 775, "BUSIBOOK NAIROBI E-TICKET")
        c.setFont("Helvetica", 11)
        c.drawString(70, 745, f"PASSENGER: {name} ({gender})")
        c.drawString(70, 725, f"VEHICLE: {v_type} | SEAT: {seat}")
        c.drawString(70, 705, f"ROUTE: {route}")
        c.drawString(70, 685, f"DEPARTURE TIME: {travel_time}")
        c.drawString(70, 665, f"BOOKED ON: {booking_date}")
        c.drawString(70, 645, f"FARE: KES {final_fare} | M-PESA: {mpesa}")
        
        for i in range(0, 60, 6):
            for j in range(0, 60, 6):
                if random.choice([True, False]): c.rect(460+i, 600+j, 6, 6, fill=1)
        c.save()

        return redirect(url_for('view_receipt', ticket_id=ticket_id))
    except mysql.connector.Error as err:
        return f"Database Error: {err}. Please check your DB_CONFIG."
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'nairobi2026':
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    tickets = cursor.fetchall()
    conn.close()
    return render_template('admin.html', tickets=tickets)

@app.route('/view_receipt/<int:ticket_id>')
def view_receipt(ticket_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    return render_template('receipt.html', t=ticket)

@app.route('/download/<int:ticket_id>')
def download_ticket(ticket_id):
    return send_file(f"tickets/Ticket_{ticket_id}.pdf", as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)