from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import sqlite3
from datetime import datetime
import os
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database initialization
def init_db():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT NOT NULL,
            date TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            bus_number TEXT NOT NULL,
            total_amount REAL NOT NULL
        )
    """)
    conn.commit()

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Billing page
@app.route("/billing", methods=["GET", "POST"])
def billing():
    if request.method == "POST":
        # Get form data
        customer_name = request.form.get("customer_name")
        bus_number = request.form.get("bus_number")
        bill_number = generate_bill_number()
        date = datetime.now().strftime("%Y-%m-%d")
        total_amount = float(request.form.get("total_amount"))

        # Save to database
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sales (bill_number, date, customer_name, bus_number, total_amount)
            VALUES (?, ?, ?, ?, ?)
        """, (bill_number, date, customer_name, bus_number, total_amount))
        conn.commit()
        conn.close()

        flash("Bill generated successfully!", "success")
        return redirect(url_for("billing"))

    return render_template("billing.html")

@app.route("/sales")
def sales():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bill_number, date, customer_name, bus_number, total_amount FROM sales")
    rows = cursor.fetchall()
    conn.close()
    return render_template("sales.html", sales_data=rows)

def generate_bill_number():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    conn.close()
    return f"BILL{count + 1:05d}"

@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    data = request.get_json()
    
    # Create PDF with FPDF
    pdf = FPDF()
    pdf.add_page()

    # Add logos with error handling
    logo_path = "logo.png"
    logo_path1 = "Qr.png"
    try:
        pdf.image(logo_path, x=10, y=8, w=30)
    except Exception as e:
        flash("Shop logo not found. Continuing without logo.", "warning")

    try:
        pdf.image(logo_path1, x=153, y=40, w=35)
    except Exception as e:
        flash("QR code image not found. Continuing without QR code.", "warning")

    # Shop Details
    pdf.set_font("Times", size=15, style='B')
    pdf.cell(200, 10, txt="Chhotu Mechanic", ln=True, align="C")
    pdf.cell(200, 10, txt="Jagatpur Road, Wazirabad, Delhi-110084", ln=True, align="C")
    pdf.set_font("Times", size=10, style='B')
    pdf.cell(200, 10, txt="Mobile Number: 9560106413", ln=True, align="C")

    # Customer & Bill Info with better spacing
    pdf.cell(200, 10, ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 5, txt=f"Customer: {data['customer_name']}", ln=True, align="L")
    
    pdf.set_font("Times", size=12, style='B')
    pdf.cell(200, 5, txt=f"Bus Number: {data['bus_number']}", ln=True, align="L")
    pdf.cell(200, 5, txt=f"Date: {data['date']}", ln=True, align="L")
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 5, txt=f"Bill Number: {data['bill_number']}", ln=True, align="L")

    # Item Table Header with better spacing
    pdf.cell(200, 10, ln=True)
    pdf.set_font("Arial", size=10, style='B')
    pdf.cell(10, 10, "S.No", border=1, align="C")
    pdf.cell(106, 10, "Item", border=1, align="C")
    pdf.cell(10, 10, "QTY", border=1, align="C")
    pdf.cell(26, 10, "Price", border=1, align="C")
    pdf.cell(26, 10, "Total", border=1, align="C")
    pdf.ln(10)

    # Item Table Content with improved error handling
    total_amount = 0
    pdf.set_font("Arial", size=10)
    
    for i, item in enumerate(data['items']):
        try:
            # Add item details
            pdf.cell(10, 10, str(i + 1), border=1, align="C")
            pdf.cell(106, 10, str(item['name']), border=1, align="L")
            pdf.cell(10, 10, str(item['quantity']), border=1, align="C")
            pdf.cell(26, 10, f"Rs.{item['price']:.2f}", border=1, align="C")
            pdf.cell(26, 10, f"Rs.{item['total']:.2f}", border=1, align="C")
            pdf.ln(10)
            
            total_amount += float(item['total'])
            
        except Exception as e:
            flash(f"Error processing item {i + 1}: {str(e)}", "warning")
            continue

    # Total Amount with better formatting
    pdf.cell(200, 3, ln=True)
    pdf.set_font("Arial", size=11, style='B')
    pdf.cell(126, 10, "Total Amount", border=1, align="C")
    pdf.cell(52, 10, f"Rs.{total_amount:.2f}", border=1, align="C")

    # Footer section with improved formatting
    pdf.cell(200, 8, ln=True)
    pdf.set_font("Arial", size=6, style="BU")
    pdf.cell(200, 10, txt="Terms & Instructions:", ln=True, align="L")
    
    pdf.set_font("Arial", size=6)
    pdf.cell(200, 0, txt="1. This is an electronically generated bill", ln=True, align="L")
    pdf.cell(200, 6, txt="2. All prices are inclusive of applicable taxes", ln=True, align="L")
    pdf.cell(200, 0, txt="3. For any queries, please contact: 9560106413", ln=True, align="L")

    # Save the PDF
    output_path = os.path.join('static', 'bills', f"bill_{data['bill_number']}.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)

    return jsonify(f"/static/bills/bill_{data['bill_number']}.pdf")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)