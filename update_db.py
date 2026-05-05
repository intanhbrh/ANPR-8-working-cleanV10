from ANPRmodel.database.database import SQL_database
import os
from colorama import Fore, init

# Initialize colorama
init()

def update_database():
    try:
        db = SQL_database(os.path.join(os.path.dirname(__file__), 'ANPRmodel', 'database', 'database.db'))
        
        # Clear existing data
        print(Fore.YELLOW + 'Clearing existing database...' + Fore.RESET)
        if db.clear_database():
            print(Fore.GREEN + 'Database cleared successfully' + Fore.RESET)
        else:
            print(Fore.RED + 'Failed to clear database' + Fore.RESET)
            return
            
        # Update with new data
        print(Fore.YELLOW + 'Updating database with new data...' + Fore.RESET)
        db.update_database(r'Vehicle Registration 2024_25.xlsx')
        print(Fore.GREEN + 'Database updated successfully' + Fore.RESET)
        
    except Exception as e:
        print(Fore.RED + f'Error: {str(e)}' + Fore.RESET)

if __name__ == '__main__':
    update_database()