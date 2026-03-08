cursor.execute("SELECT * FROM options_data")
rows = cursor.fetchall()

for row in rows:
    process(row)