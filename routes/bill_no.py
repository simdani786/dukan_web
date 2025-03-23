from flask import Blueprint, render_template, jsonify
import sqlite3
from .utils import generate_bill_number

bill_number_bp = Blueprint('bill_no', __name__)

@bill_number_bp.route("/get_bill_number", methods=["GET"])
def get_bill_number():
    bill_number = generate_bill_number()
    return jsonify({"bill_number": bill_number})
