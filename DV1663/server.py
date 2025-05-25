#!/usr/bin/python

from flask import Flask, request, jsonify, render_template
import sqlite3  # Database

app = Flask(__name__)

def get_gods_adventures():
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

def get_main_characters():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM main_character")
    data = cursor.fetchall()
    conn.close()
    return data

def get_adventures():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM adventures")
    data = cursor.fetchall()
    conn.close()
    return data

def get_side_characters():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM side_character")
    data = cursor.fetchall()
    conn.close()
    return data

def get_gods():
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gods")
    data = cursor.fetchall()
    conn.close()
    return data

def add_adventure(adventure_data):
    conn = sqlite3.connect('projekt_dv1663.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(cursor.fetchall())

        cursor.execute("""
                        INSERT OR REPLACE INTO adventures (Goal, Brief, name)
                        VALUES (?, ?, ?)
                        """, (adventure_data['goal'], adventure_data['brief'], adventure_data['name']))
        
        adventure_id = cursor.lastrowid
        if adventure_id is None:
            adventure_id = adventure_data['name']
        for hero in adventure_data.get('heroes', []):
            cursor.execute("""
                           INSERT INTO goes (Main_character, Adventure)
                           VALUES (?, ?)
                           """, (hero, adventure_data['name']))
        # Assuming 'adventure_data' is already a Python dict from the JSON body
        gods_data = adventure_data.get("gods", {})

        # Insert each god-action pair into the help_or_hinder table
        for god, info in gods_data.items():
            action = info.get("does")  # should be 'helps' or 'hinders'
            if action in ("helps", "hinders"):
                cursor.execute("""
                    INSERT INTO help_or_hinder (Name, ID, does)
                    VALUES (?, ?, ?)
                """, (god, hero, action))  # 'hero' must be defined in the loop/context


        conn.commit()
        print("success!")
    except sqlite3.Error as e:
        conn.rollback()
        print("Error during adventure insertion: ", e)
    finally:
        conn.close()

# Routes
@app.route('/')
def form():
    return render_template('form.html', gods = get_gods())

@app.route('/gods_adventures')
def gods_adventures():
    return jsonify(get_gods_adventures())

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

@app.route('/main_characters')
def main_characters():
    return jsonify(get_main_characters())

@app.route('/adventures')
def adventures():
    return jsonify(get_adventures())

@app.route('/side_characters')
def side_characters():
    return jsonify(get_side_characters())


@app.route('/gods')
def gods():
    return jsonify(get_gods())

@app.route("/add_adventure", methods=["POST"])
def add_adventure_route():
    data = request.get_json()
    try:
        add_adventure(data)
        return "Adventure added successfully"
    except Exception as e:
        print("error: ", e)
        return "failed to add adventure: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
