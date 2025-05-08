from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('projekt_dv1663.db') 
    conn.row_factory = sqlite3.Row  # to return rows as dictionaries
    return conn

# 1. Function to Get Heroes by Trait
@app.route('/get_heroes_by_trait', methods=['GET'])
def get_heroes_by_trait():
    trait = request.args.get('trait')  
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Trait FROM main_character WHERE Trait = ?", (trait,))
    heroes = cursor.fetchall()
    conn.close()
    
    heroes_list = [{"Name": hero["Name"], "Trait": hero["Trait"]} for hero in heroes]
    return jsonify(heroes_list)

# 2. Procedure to Assign Relation (as a POST request)
@app.route('/assign_relation', methods=['POST'])
def assign_relation():
    hero_name = request.json.get('hero_name')
    god_name = request.json.get('god_name')
    relation_type = request.json.get('relation_type')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO relation (Main_character, God, Relation)
        VALUES (?, ?, ?)
    """, (hero_name, god_name, relation_type))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Relation assigned successfully!"}), 201

# 3. Query to Get the Number of Heroes Each God Has a Relation With
@app.route('/heroes_count_per_god', methods=['GET'])
def heroes_count_per_god():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT God, COUNT(Main_character) AS Number_of_Heroes
        FROM relation
        GROUP BY God
        ORDER BY Number_of_Heroes DESC
    """)
    god_counts = cursor.fetchall()
    conn.close()
    
    god_counts_list = [{"God": god["God"], "Number_of_Heroes": god["Number_of_Heroes"]} for god in god_counts]
    return jsonify(god_counts_list)

# 4. Query to Get Heroes Without Divine Parents
@app.route('/heroes_without_divine_parents', methods=['GET'])
def heroes_without_divine_parents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT main_character.Name, relation.God
        FROM main_character
        LEFT JOIN relation ON main_character.Name = relation.Main_character
        WHERE relation.Relation <> 'Father' AND relation.Relation <> 'Mother'
    """)
    heroes = cursor.fetchall()
    conn.close()
    
    heroes_list = [{"Name": hero["Name"], "God": hero["God"]} for hero in heroes]
    return jsonify(heroes_list)

@app.route('/')
def index():
    return "Welcome to the Greek Mythology API!"

if __name__ == '__main__':
    app.run(debug=True)
