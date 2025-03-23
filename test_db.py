import sqlite3
import random
from datetime import datetime, timedelta

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('sales.db')
cursor = conn.cursor()

# Create the sales table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT NOT NULL,
    date TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    bus_number TEXT NOT NULL,
    total_amount REAL NOT NULL
)
''')

# Function to generate random sales data
def generate_sales_data(num_records):
    sales_data = []
    start_date = datetime(2023, 1, 1)  # Start date for random date generation
    customers = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hank"]
    bus_numbers = ["BUS101", "BUS102", "BUS103", "BUS104", "BUS105"]

    for i in range(num_records):
        bill_number = f"{1000 + i}"  # Generate unique bill numbers
        date = (start_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")  # Random date in 2023
        customer_name = random.choice(customers)  # Random customer name
        bus_number = random.choice(bus_numbers)  # Random bus number
        total_amount = round(random.uniform(50, 500), 2)  # Random total amount between 50 and 500

        sales_data.append((bill_number, date, customer_name, bus_number, total_amount))

    return sales_data

# Define the number of records to generate
num_records = 1000  # Generate 1000 sales records

# Generate random sales data
test_data = generate_sales_data(num_records)

# Insert data into the sales table
cursor.executemany('''
INSERT INTO sales (bill_number, date, customer_name, bus_number, total_amount)
VALUES (?, ?, ?, ?, ?)
''', test_data)

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Inserted {num_records} sales records into the database.")