from database import SQL_database
import os

# Run from working directory (/ANPR-8_Working)
root = os.path.join('ANPRmodel', 'database')
if os.path.exists(os.path.join(root, 'database.db')):
    os.remove(os.path.join(root, 'database.db'))
db = SQL_database(os.path.join(root, 'database.db'))
db.create_table()
db.update_database(os.path.join(root, 'Vehicle Registration 2024_25 - Term 1 (Responses).xlsx'))
