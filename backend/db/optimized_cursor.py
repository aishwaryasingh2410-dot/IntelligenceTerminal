cursor.execute("SELECT * FROM options_data")

while True:
    rows = cursor.fetchmany(1000)

    if not rows:
        break

    process(rows)
