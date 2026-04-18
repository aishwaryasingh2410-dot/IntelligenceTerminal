from backend.queries.options_queries import get_options_cursor

data = get_options_cursor(limit=5)

for d in data:
    print(d)
