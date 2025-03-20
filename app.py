from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import sqlite3
from datetime import datetime
import os
from fpdf import FPDF
import json
from collections import defaultdict

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
    return render_template("monthly_sales.html")

# Billing page
@app.route("/billing", methods=["GET", "POST"])
def billing():
    if request.method == "POST":
        # Get form data
        customer_name = request.form.get("customer_name")
        bus_number = request.form.get("bus_number")
        bill_number = generate_bill_number()  # Generate a new bill number
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

@app.route("/monthly_sales")
def monthly_sales():
    return render_template("monthly_sales.html")

@app.route("/api/monthly_sales_data")
def monthly_sales_data():
    try:
        # Connect to the database
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        
        # Get the sales data grouped by month
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(total_amount) as total_sales
            FROM 
                sales
            GROUP BY 
                strftime('%Y-%m', date)
            ORDER BY 
                month ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Format the data for Chart.js
        months = []
        sales_amounts = []
        
        for row in rows:
            month = row[0]  # Format: YYYY-MM
            year_month = month.split('-')
            # Convert month number to name (e.g., 01 to January)
            month_name = datetime.strptime(month, '%Y-%m').strftime('%b %Y')
            months.append(month_name)
            sales_amounts.append(float(row[1]))
        
        return jsonify({
            'labels': months,
            'data': sales_amounts
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_bill_number():
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT bill_number FROM sales ORDER BY id DESC LIMIT 1")
    last_bill = cursor.fetchone()
    
    if last_bill:
        last_number = int(last_bill[0])  
        new_number = last_number + 1
    else:
        new_number = 1
    
    conn.close()
    return f"{new_number:05d}"  

@app.route("/get_bill_number", methods=["GET"])
def get_bill_number():
    bill_number = generate_bill_number()
    return jsonify({"bill_number": bill_number})



@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    data = request.get_json()
    
    # Generate a new bill number
    bill_number = generate_bill_number()
    print("/generate_pdf",bill_number)
    
    # Save to database
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales (bill_number, date, customer_name, bus_number, total_amount)
        VALUES (?, ?, ?, ?, ?)
    """, (
        bill_number,
        data['date'],
        data['customer_name'],
        data['bus_number'],
        sum(float(item['total']) for item in data['items'])  
    ))
    conn.commit()
    conn.close()
    
    # Create PDF with FPDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set margins individually instead of using set_margin
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_top_margin(10)

    # Add logos with error handling
    logo_path = "logo.png"
    logo_path1 = "Qr.png"
    try:
        pdf.image(logo_path, x=10, y=8, w=30)
    except Exception as e:
        flash("Shop logo not found. Continuing without logo.", "warning")

    try:
        pdf.image(logo_path1, x=160, y=55, w=30)
    except Exception as e:
        flash("QR code image not found. Continuing without QR code.", "warning")

    # Shop Details
    pdf.set_font("Times", size=18, style='B')
    pdf.cell(190, 10, txt="CHHOTU MECHANIC", ln=True, align="C")
    pdf.set_font("Times", size=12)
    pdf.cell(190, 6, txt="Jagatpur Road, Wazirabad, Delhi-110084", ln=True, align="C")
    pdf.cell(190, 6, txt="Mobile Number: 9560106413", ln=True, align="C")
    
    # Separator line
    pdf.line(10, 42, 200, 42)
    pdf.ln(10)

    # Invoice title
    pdf.set_font("Times", size=14, style='B')
    pdf.cell(190, 10, txt="INVOICE", ln=True, align="C")
    pdf.ln(5)

    # Customer & Bill Info with better layout
    pdf.set_font("Arial", size=10,style='B')
    
    # Left side info
    pdf.set_fill_color(245, 245, 245)
    col_width = 190
    pdf.cell(col_width, 6, txt=f"Customer:  {data['customer_name']}", ln=True,align="L")
    pdf.cell(col_width, 6, txt=f"Bill Number:   {bill_number}", ln=True, align="L")
    pdf.cell(col_width, 6, txt=f"Bus Number:    {data['bus_number']}",ln=True, align="L")
    pdf.cell(col_width, 6, txt=f"Date:  {data['date']}", ln=True, align="L")
    
    pdf.ln(10)

    # Item Table Header
    pdf.set_font("Arial", size=10, style='B')
    pdf.set_fill_color(220, 220, 220)
    
    # Define column widths for better alignment
    col_widths = [15, 85, 20, 30, 30]
    
    pdf.cell(col_widths[0], 10, "S.No", border=1, align="C", fill=True)
    pdf.cell(col_widths[1], 10, "Item", border=1, align="C", fill=True)
    pdf.cell(col_widths[2], 10, "QTY", border=1, align="C", fill=True)
    pdf.cell(col_widths[3], 10, "Price", border=1, align="C", fill=True)
    pdf.cell(col_widths[4], 10, "Total", border=1, align="C", fill=True)
    pdf.ln(10)

    # Item Table Content with improved alignment
    total_amount = 0
    pdf.set_font("Arial", size=10)
    pdf.set_fill_color(255, 255, 255)
    
    # Alternate row colors for better readability
    row_color = False
    
    for i, item in enumerate(data['items']):
        try:
            # Set alternate row colors
            if row_color:
                pdf.set_fill_color(242, 242, 242)
            else:
                pdf.set_fill_color(255, 255, 255)
            row_color = not row_color
            
            # Add item details
            pdf.cell(col_widths[0], 10, str(i + 1), border=1, align="C", fill=True)
            pdf.cell(col_widths[1], 10, str(item['name']), border=1, align="C", fill=True)
            pdf.cell(col_widths[2], 10, str(item['quantity']), border=1, align="C", fill=True)
            pdf.cell(col_widths[3], 10, f"Rs.{float(item['price']):.2f}", border=1, align="C", fill=True)
            pdf.cell(col_widths[4], 10, f"Rs.{float(item['total']):.2f}", border=1, align="C", fill=True)
            pdf.ln(10)
            
            total_amount += float(item['total'])
            
        except Exception as e:
            flash(f"Error processing item {i + 1}: {str(e)}", "warning")
            continue

    # Total Amount with better formatting
    pdf.ln(2)
    pdf.set_font("Arial", size=11, style='B')
    pdf.cell(col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], 10, "Total Amount", border=1, align="C", fill=False)
    pdf.cell(col_widths[4], 10, f"Rs.{total_amount:.2f}", border=1, align="C", fill=False)

    # Footer section with improved formatting
    pdf.ln(15)
    pdf.set_font("Arial", size=8, style="B")
    pdf.cell(190, 6, txt="Terms & Instructions:", ln=True, align="L")
    
    pdf.set_font("Arial", size=8)
    pdf.cell(190, 5, txt="1. This is an electronically generated bill", ln=True, align="L")
    pdf.cell(190, 5, txt="2. All prices are inclusive of applicable taxes", ln=True, align="L")
    pdf.cell(190, 5, txt="3. For any queries, please contact: 9560106413", ln=True, align="L")
    
    # Add signature section
    pdf.ln(15)
    pdf.line(140, pdf.get_y(), 190, pdf.get_y())
    pdf.set_font("Arial", size=8, style="I")
    pdf.cell(170, 5, txt="Authorized Signature", ln=True, align="R")

    # Save the PDF
    output_path = os.path.join('static', 'bills', f"bill_{bill_number}.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)

    return jsonify(f"/static/bills/bill_{bill_number}.pdf")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)