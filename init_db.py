import sqlite3

connection = sqlite3.connect('products.db')


with open('schema.sql') as f:
    connection.executescript(f.read())
