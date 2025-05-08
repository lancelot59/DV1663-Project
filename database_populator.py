import sqlite3

conn = sqlite3.connect('projekt_dv1663.db')
cur = conn.cursor()

main_characters = [
    ("Achilles", None, "greek hero of the trojan war", "invulnerability, speed", "Pride", "Spear"),
    ("Odysseus", "Ulysses", "cunning king of ithaca", "intellect", "cunning", "bow"),
    ("Heracles", "Hercules", "Sone of Zeus, Primary slayer of beasts", "super strenght", "Bravery", "Club and Bow")
]

cur.executemany('''
                INSERT INTO mainCharacter (name, alias, description, special_skill, trait, weapon)
                VALUES (?,?,?,?,?,?))
                ''', main_characters)

conn.commit()
conn.close()