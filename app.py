from flask import Flask, render_template
from init_db import init_db
from routes.billing import billing_bp
from routes.sales import sales_bp
from routes.pdf import pdf_bp
from routes.bill_no import bill_number_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize Database
init_db()

# Register Blueprints
app.register_blueprint(bill_number_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(pdf_bp)

# Home Page
@app.route("/")
def home():
    return render_template("monthly_sales.html")

if __name__ == "__main__":
    app.run(debug=True)
