#!/usr/bin/python

from flask import Flask, request, jsonify, render_template
import sqlite3  # Database

app = Flask(__name__)

# Connect to SQLite and get city names
def get_gods():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute( """SELECT g.name AS God, COUNT(r.Main_character) AS Number_of_Heroes, COUNT(h.ID) AS Helps_or_Hinders
                        FROM gods g
                        LEFT JOIN relation r ON g.name = r.God
                        LEFT JOIN help_or_hinder h ON g.name = h.name
                        GROUP BY g.name
                        ORDER BY Number_of_Heroes DESC;""")
    gods = cursor.fetchall()
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
