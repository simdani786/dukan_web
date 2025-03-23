from flask import Blueprint, request, render_template, redirect, url_for, flash
import sqlite3
from datetime import datetime
from .utils import generate_bill_number

billing_bp = Blueprint('billing', __name__)

@billing_bp.route("/billing", methods=["GET", "POST"])
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
