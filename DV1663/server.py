#!/usr/bin/python

from flask import Flask, request, jsonify, render_template
import sqlite3  # Database

app = Flask(__name__)

# Connect to SQLite and get city names
def get_gods():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM gods")
    gods = [row[0] for row in cursor.fetchall()]
    conn.close()
    return gods

def get_details(item_id):
    conn = sqlite3.connect('projekt_dv1663.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Safe query using parameter substitution to avoid SQL injection
    cursor.execute("SELECT * FROM gods WHERE name = ?", (item_id,))
    row = [tuple(elements) for elements in cursor.fetchall()]
    conn.close()
    return row

# Serve the HTML form
@app.route('/')
def form():
    return render_template('form.html', gods = get_gods())

# Serve city data for dropdown
@app.route('/gods')
def gods():
    return jsonify(get_gods())



@app.route('/details/<item_id>')
def details(item_id):
    return jsonify(get_details(item_id))

if __name__ == '__main__':
    app.run(debug=True)
