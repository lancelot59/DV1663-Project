#!/usr/bin/python

from flask import Flask, request, jsonify, render_template
import sqlite3  # Database

app = Flask(__name__)

# Connect to SQLite
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

def get_main_char_adventures():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mc.Name AS Main_Character, COUNT(g.Adventure) AS Number_of_Adventures
        FROM main_character mc
        LEFT JOIN goes g ON mc.Name = g.Main_character
        LEFT JOIN adventures a ON g.Adventure = a.name
        GROUP BY mc.Name
        ORDER BY Number_of_Adventures DESC;
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_god_interventions():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.name AS God, COUNT(h.name) AS Interventions
        FROM help_or_hinder h
        GROUP BY h.name
        ORDER BY Interventions DESC;
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_god_summary(god_name):
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()

    # Get god's core details
    cursor.execute("""
        SELECT Name, Father, Mother, God_of
        FROM gods
        WHERE Name = ?
    """, (god_name,))
    god = cursor.fetchone()

    if not god:
        conn.close()
        return f"No information found for god '{god_name}'."

    name, father, mother, domain = god

    # Count linked heroes
    cursor.execute("""
        SELECT COUNT(DISTINCT r.Main_character)
        FROM relation r
        WHERE r.God = ?
    """, (god_name,))
    hero_count = cursor.fetchone()[0]

    # Count number of adventures they help or hinder
    cursor.execute("""
        SELECT COUNT(DISTINCT h.ID)
        FROM help_or_hinder h
        WHERE h.Name = ?
    """, (god_name,))
    intervention_count = cursor.fetchone()[0]

    conn.close()

    # Build the full summary
    summary = (
        f"{name} God(dess) of {domain} is the child of {father} and {mother}.\n"
        f"They are associated with {hero_count} main character{'s' if hero_count != 1 else ''}, "
        f"and have intervened in {intervention_count} adventure{'s' if intervention_count != 1 else ''}."
    )
    return summary


def setup_trigger():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS character_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS log_new_main_character
        AFTER INSERT ON main_character
        BEGIN
            INSERT INTO character_log(name) VALUES (NEW.name);
        END;
    """)
    conn.commit()
    conn.close()

def add_main_character(data):
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO main_character (Name, Father_Name, Alias, Trait, Weapon, Skill)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get('name'),
        data.get('father_name'),
        data.get('alias'),
        data.get('trait'),
        data.get('weapon'),
        data.get('skill')
    ))

    conn.commit()
    conn.close()
    return f"Main character '{data.get('name')}' added."


# Routes
@app.route('/')
def form():
    return render_template('form.html', gods = get_gods())

@app.route('/gods')
def gods():
    return jsonify(get_gods())

@app.route('/main_char_adventures')
def main_char_adventures():
    return jsonify(get_main_char_adventures())

@app.route('/god_interventions')
def god_interventions():
    return jsonify(get_god_interventions())

@app.route('/god_summary/<god_name>')
def god_summary(god_name):
    return jsonify({"summary": get_god_summary(god_name)})

@app.route('/add_main_character', methods=['POST'])
def add_character():
    data = request.json
    return jsonify({"message": add_main_character(data)})



@app.route('/details/<item_id>')
def details(item_id):
    return jsonify(get_details(item_id))





if __name__ == '__main__':
    app.run(debug=True)
