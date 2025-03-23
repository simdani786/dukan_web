from flask import Blueprint, request, jsonify, flash
import sqlite3
from fpdf import FPDF
import os
from .utils import generate_bill_number
from datetime import datetime

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route("/generate_pdf", methods=["POST"])
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

    pdf.set_font("Arial", size=12,style='B')
    pdf.cell(40, 6, "Customer", 0, 0)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(60, 6,data['customer_name'], 0, 1)

    pdf.set_font("Arial", size=12,style='B')
    pdf.cell(40, 6, "Bill Number", 0, 0)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(60, 6,bill_number, 0, 1)

    pdf.set_font("Arial", size=12,style='B')
    pdf.cell(40, 6, "Bus Number", 0, 0)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(60, 6,data['bus_number'], 0, 1)


    pdf.set_font("Arial", size=12,style='B')
    pdf.cell(40, 6, "Date", 0, 0)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(60, 6,data['date'], 0, 1)
    
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
            # # Set alternate row colors
            # if row_color:
            #     pdf.set_fill_color(242, 242, 242)
            # else:
            #     pdf.set_fill_color(255, 255, 255)
            # row_color = not row_color
            
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

    pdf.ln(15)

    # Payment information
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10, style='B')
    pdf.cell(190, 5, "Payment Information", 0, 1, 'L')
    
    pdf.set_font("Arial", size=9)
    pdf.cell(40, 6, "Bank Name:", 0, 0)
    pdf.set_font("Arial", size=9, style='B')
    pdf.cell(60, 6, "State Bank of India", 0, 1)
    
    pdf.set_font("Arial", size=9)
    pdf.cell(40, 6, "Account Number:", 0, 0)
    pdf.set_font("Arial", size=9, style='B')
    pdf.cell(60, 6, "1234567890", 0, 1)
    
    pdf.set_font("Arial", size=9)
    pdf.cell(40, 6, "IFSC Code:", 0, 0)
    pdf.set_font("Arial", size=9, style='B')
    pdf.cell(60, 6, "SBIN0123456", 0, 1)

 # Terms & Conditions 
    pdf.ln(5)
    pdf.set_fill_color(242, 242, 242)
    pdf.rect(10, pdf.get_y(), 190, 35, 'F')
    
    pdf.set_font("Arial", size=10, style="B")
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 8, "Terms & Conditions:", 0, 1, 'L')
    
    pdf.set_text_color(80, 80, 80)
    pdf.set_font("Arial", size=8)
    pdf.cell(190, 5, "1. This is an electronically generated invoice and does not require signature.", 0, 1, 'L')
    pdf.cell(190, 5, "2. All prices are inclusive of applicable taxes unless specified otherwise.", 0, 1, 'L')
    pdf.cell(190, 5, "3. For inquiries regarding this invoice, please contact: +91 9560106413", 0, 1, 'L')



    # Add signature section
    pdf.ln(30)
    pdf.line(140, pdf.get_y(), 190, pdf.get_y())
    pdf.set_font("Arial", size=8, style="I")
    pdf.cell(170, 5, txt="Authorized Signature", ln=True, align="R")

    # Add timestamp in small text
    pdf.set_font("Arial", size=7)
    pdf.set_text_color(150, 150, 150)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(190, 20, f"Generated on: {current_time}", 0, 1, "C")

    # Save the PDF
    output_path = os.path.join('static', 'bills', f"bill_{bill_number}.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)

    return jsonify(f"/static/bills/bill_{bill_number}.pdf")
