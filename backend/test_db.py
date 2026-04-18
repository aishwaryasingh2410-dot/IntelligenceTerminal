from backend.db.connection import options_chain
data = options_chain.find_one()

print("Connection Successful")
print(data)