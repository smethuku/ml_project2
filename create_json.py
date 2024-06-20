import json

# Create a list of dictionaries with one containing a multiline string
data = [
    {
        "sql": "select something",
        "email": "to@someemail.com",
        "sub": "1st email"
    },
    {
        "sql": "update something",
        "email": "to@someemail.com",
        "sub": "2nd email"
    },
    {
        "sql": """Select top 10 * from table1
where item = 1""",
        "email": "anotheremail@domain.com",
        "sub": "3rd email with multiline SQL"
    }
]

# Define the path to the JSON file
file_path = 'output.json'

# Write the data to the JSON file
with open(file_path, 'w') as file:
    json.dump(data, file, indent=4)

print(f"Data written to {file_path}")
