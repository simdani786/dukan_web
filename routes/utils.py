import sqlite3

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