from flask import Flask, render_template, session, redirect
from datetime import timedelta
from init_db import init_db
from routes.billing import billing_bp
from routes.sales import sales_bp
from routes.pdf import pdf_bp
from routes.bill_no import bill_number_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.permanent_session_lifetime = timedelta(days=30)  # For "remember me" functionality

# Initialize Database
init_db()

# Register Blueprints
app.register_blueprint(bill_number_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(pdf_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    if 'username' not in session:
        return redirect('/login')
    return render_template("monthly_sales.html")

if __name__ == "__main__":
    app.run(debug=True)