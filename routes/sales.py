from flask import Blueprint, render_template, jsonify
import sqlite3
from datetime import datetime

sales_bp = Blueprint('sales', __name__)

# Helper functions for the template
def format_currency(value):
    """Format a number as currency with thousand separators"""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

def format_date(date_str):
    """Format date string to a more readable format"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%b %d, %Y')  # Mar 21, 2025 format
    except ValueError:
        return date_str

def get_month_name(month_num):
    """Convert month number to month name"""
    try:
        month_num = int(month_num)
        return datetime(2025, month_num, 1).strftime('%B')  # Full month name
    except ValueError:
        return month_num

@sales_bp.route("/sales")
def sales_data():
    # Connect to the database
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    # Fetch all sales data using * to get all columns
    cursor.execute('SELECT * FROM sales ORDER BY DATE(date) ASC')
    sales_data = cursor.fetchall()
    # if sales_data:
    #     print("First row sample:", sales_data[0])

    total_sales =0 
    count=0   

    for row in sales_data:
        count=count+1
        total_sales=total_sales+row[5]

    Totalsales=int(total_sales)
    avgsales=Totalsales/count

    
    # Extract unique years and months from the data
    years = []
    months = []
    
    for row in sales_data:
        if len(row) > 1 and row[2] and isinstance(row[2], str) and '-' in row[2]:
            date_parts = row[2].split('-')
            if len(date_parts) >= 2:
                years.append(date_parts[0])
                months.append(date_parts[1])
    
    years = sorted(set(years))
    months = sorted(set(months))
    
    conn.close()

    return render_template(
        'sales.html', 
        sales_data=sales_data, 
        years=years, 
        months=months,
        format_currency=format_currency,
        formatDate=format_date,
        getMonthName=get_month_name,
        Totalsales=Totalsales,
        count=count,
        avgsales=avgsales

    )



@sales_bp.route("/monthly_sales_data")
def monthly_sales_data():
    try:
        conn = sqlite3.connect("sales.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(total_amount) as total_sales
            FROM sales
            GROUP BY month
            ORDER BY month ASC
        """)
        rows = cursor.fetchall()
        conn.close()

        months = [datetime.strptime(row[0], '%Y-%m').strftime('%b %Y') for row in rows]
        sales_amounts = [float(row[1]) for row in rows]

        return jsonify({'labels': months, 'data': sales_amounts})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
