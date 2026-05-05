import sqlite3
import pandas as pd 
import os
import numpy as np
import uuid
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQL_database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.parent_table = 'parent_vehicle_reg'

    def create_connection(self):
        try:
            sqliteConnection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = sqliteConnection.cursor()
            logger.info('Database has been initialized')
            
            cursor.execute('select sqlite_version();')
            result = cursor.fetchall()
            logger.info(f'SQLite Version is {result}')
    
            return sqliteConnection, cursor
        
        except sqlite3.Error as error:
            logger.error(f'Error occurred [create_connection] - {error}')
            raise

    def create_table(self):
        sqliteConnection, cursor = self.create_connection()
        create_table = f'''
            CREATE TABLE {self.parent_table}(
            uuid TEXT PRIMARY KEY,
            email_address TEXT,
            parent_name TEXT,
            parent_contact INTEGER,
            child_1_name TEXT,
            child_1_year TEXT,
            child_2_name TEXT,
            child_2_year TEXT,
            child_3_name TEXT,
            child_3_year TEXT,
            child_4_name TEXT,
            child_4_year TEXT,
            car_1_num TEXT,
            car_1_model TEXT,
            car_2_num TEXT,
            car_2_model TEXT,
            car_3_num TEXT,
            car_3_model TEXT,
            car_4_num TEXT,
            car_4_model TEXT,
            car_5_num TEXT,
            car_5_model TEXT,
            car_6_num TEXT,
            car_6_model TEXT)'''
        cursor.execute(create_table)
        self.close_connection(sqliteConnection, cursor)

    def close_connection(self, sqliteConnection, cursor):
        sqliteConnection.commit()
        cursor.close()
        if sqliteConnection:
            sqliteConnection.close()
            logger.info('SQLite Connection closed')

    def format_xlsx(self, csv_path):
        logger.info('Formatting Spreadsheet')
        data = pd.read_excel(csv_path)
        
        # Column mappings dictionary
        column_mappings = {
            'Timestamp': 'timestamp',
            'Email address': 'email_address',
            'I am registering my vehicle as a': 'staff_parent',
            'Parent Full Name': 'parent_name',
            'Parent Contact Number' : 'parent_contact', 
            'Child 1' : 'child_1_name', 
            'Select the year group your child(1) is in' : 'child_1_year', 
            'Child 2' : 'child_2_name',
            'Select the year group your child(2) is in' : 'child_2_year', 
            'Child 3' : 'child_3_name',
            'Select the year group your child(3) is in' : 'child_3_year', 
            'Child 4' : 'child_4_name',
            'Select the year group your child(4) is in' : 'child_4_year',
            'Vehicle Registration Number 1 (Car Plate)' : 'car_1_num', 
            'Car Model 1' : 'car_1_model',
            'Vehicle Registration Number 2 (Car Plate)' : 'car_2_num', 
            'Car Model 2' : 'car_2_model',
            'Vehicle Registration Number 3 (Car Plate)' : 'car_3_num',
            'Car Model 3' : 'car_3_model',
            'Do you require more than 3 car stickers?' : 'more_than_3',
            'Vehicle Registration Number 1 (Additional)' : 'car_4_num',
            'Car Model 1 (Additional)' : 'car_4_model',
            'Vehicle Registration Number 2 (Additional)' : 'car_5_num',
            'Car Model 2 (Additional)' : 'car_5_model',
            'Vehicle Registration Number 3 (Additional)' : 'car_6_num',
            'Car Model 3 (Additional)' : 'car_6_model', 
            'Staff Full Name' : 'staff_name', 
            'Staff Contact Number' : 'staff_contact',
            'Department' : 'department', 
            'Vehicle Registration Number 1 (Car Plate).1' : 'staff_car_1_num',
            'Car Model 1.1' : 'staff_car_1_model', 
            'Vehicle Registration Number 2 (Car Plate).1' :'staff_car_2_num',
            'Car Model 2.1' : 'staff_car_2_model'
        }
        data.rename(columns=column_mappings, inplace=True)

        # Remove staff entries
        data = data.drop(data[data['staff_parent'] == "Staff"].index, axis=0)
        data = data.drop(0, axis=0).reset_index(drop=True)

        # Remove unused columns
        columns_to_drop = ['timestamp', 'staff_parent', 'more_than_3', 'staff_name',
                          'staff_contact', 'department', 'staff_car_1_num', 
                          'staff_car_1_model', 'staff_car_2_num', 'staff_car_2_model']
        data = data.drop(columns=columns_to_drop)

        # Add UUID and clean data
        data['uuid'] = [uuid.uuid4() for _ in range(len(data.index))]
        data = data.replace(np.nan, ' ', regex=True)

        # Format names and plates
        name_columns = ['child_1_name', 'child_2_name', 'child_3_name', 
                       'child_4_name', 'parent_name']
        plate_columns = [f'car_{i}_num' for i in range(1, 7)]

        for index, row in data.iterrows():
            for col in name_columns:
                data.at[index, col] = self.format_name(row[col])
            for col in plate_columns:
                data.at[index, col] = self.format_plate(row[col])

        return data

    def format_name(self, name):
        if not isinstance(name, str):
            return " "
            
        words = name.split()
        final_output = []
        for word in words:
            if word in ["A/L", "A/P", "bin"]:
                final_output.append(word)
            else:
                final_output.append(word.capitalize())
        return " ".join(final_output)

    def append_data(self, cursor, data):
        print('Appending Records')
        insert_records = f'''INSERT INTO {self.parent_table} (uuid, 
        email_address, parent_name, parent_contact, 
        child_1_name, child_1_year, child_2_name, child_2_year,
        child_3_name, child_3_year, child_4_name, child_4_year,
        car_1_num, car_1_model, car_2_num, car_2_model,
        car_3_num, car_3_model, car_4_num, car_4_model,
        car_5_num, car_5_model, car_6_num, car_6_model) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
        for index in range(0, len(data.index)):
            values = [str(data[col][index]) for col in [
                'uuid', 'email_address', 'parent_name', 'parent_contact',
                'child_1_name', 'child_1_year', 'child_2_name', 'child_2_year',
                'child_3_name', 'child_3_year', 'child_4_name', 'child_4_year',
                'car_1_num', 'car_1_model', 'car_2_num', 'car_2_model',
                'car_3_num', 'car_3_model', 'car_4_num', 'car_4_model',
                'car_5_num', 'car_5_model', 'car_6_num', 'car_6_model'
            ]]
            cursor.execute(insert_records, values)
            print(f"Inserted record for {values[2]}")  # Print parent name

    def update_database(self, path):
        sqliteConnection, cursor = self.create_connection()
        try:
            data = self.format_xlsx(path)
            self.append_data(cursor, data)
            self.read_all(cursor)
        except sqlite3.Error as error:
            print('Error occured - ', error)
        finally:
            self.close_connection(sqliteConnection, cursor)

    def read_all(self, cursor):

        statement = f'''SELECT * FROM {self.parent_table};'''     
        cursor.execute(statement)
        print("All the data")
        output = cursor.fetchall()
        for row in output:
            print(row)

    def update_cell(self, cursor, value_change, criteria):
        statement = f'''UPDATE {self.parent_table}
                        SET {value_change}
                        WHERE {criteria};'''
        try:
            cursor.execute(statement)
        except sqlite3.Error as error:
            print('Error occurred - ', error)
        
    def find_plate(self, cursor, car_plate):
        statement = f'''SELECT
                            child_1_name,
                            child_2_name,
                            child_3_name,
                            child_4_name,
                            child_1_year,
                            child_2_year,
                            child_3_year,
                            child_4_year
                        FROM {self.parent_table}
                        WHERE car_1_num == "{car_plate}" 
                           OR car_2_num == "{car_plate}"
                           OR car_3_num == "{car_plate}"
                           OR car_4_num == "{car_plate}"
                           OR car_5_num == "{car_plate}"
                           OR car_6_num == "{car_plate}";'''

        try:
            cursor.execute(statement)
            output = cursor.fetchall()
            return (output, True) if output else ("", False)
        except sqlite3.Error as error:
            logger.error(f'Error occurred [find_plate] - {error}')
            return None, False

    def format_plate(self, license_plate):
        if not isinstance(license_plate, str):
            return " "

        license_plate = re.sub(r'[^a-zA-Z0-9\s]', '', license_plate).upper()
        special_keywords = ["PUTRAJAYA", "MALAYSIA", "GOLD"]
        
        # Handle special cases
        if any(license_plate.startswith(keyword) for keyword in special_keywords):
            return license_plate
            
        # Standard format check
        if re.match(r'^[A-Z]{2}\s\d{4}\s[A-Z]$', license_plate):
            return license_plate

        # Format plate
        match = re.match(r'^([A-Z\s]+)(\d+)([A-Z\s]+)?$', license_plate)
        if not match:
            return license_plate

        letters, digits, suffix = match.groups()
        letters = letters.strip()
        letters = letters.rjust(2, 'A') if len(letters) < 2 else letters
        digits = digits.rjust(2, '0') if len(digits) < 2 else digits
        
        formatted_plate = f"{letters} {digits}"
        if suffix:
            formatted_plate += f" {suffix.strip()}"
            
        return re.sub(r'\s+', ' ', formatted_plate).strip()

    def plate_combinations(self, plate):
        carplate = plate
        whitelist = ["BAMbee", "SUKOM", "PATRIOT", "XIASEAN", "XII INAM", "X OIC", "PERFECT", "Malaysia", "GOLD"]
        blacklist = ["@", "!", "#", "$", "%", "^", "~", "*", "/", "<", ">", "{", "}", "|"]

        def similar(str1, str2):
            str1 = "".join(str1.split())
            str2 = "".join(str2.split())
            str1 = str1 + ' ' * (len(str2) - len(str1))
            str2 = str2 + ' ' * (len(str1) - len(str2))
            return sum(1.1 if i == j else 0
                        for i, j in zip(str1, str2)) / float(len(str1))

        def standardise_string(carplate):
            alpha1, number, alpha2 = "", "", ""
            carplate = list(carplate.replace(" ",""))
            #adding space between aphla and numebrs
            for i in range(len(carplate) - 1):
                if ((carplate[i].isdigit() and carplate[i + 1].isalpha()) or (carplate[i + 1].isdigit() and carplate[i].isalpha())):
                    carplate[i] = carplate[i] + " "
            carplate = "".join(carplate).upper()
            # print("Plate after adding space", carplate)
            #length validation & seperate into 3 parts for further checking
            if (len(carplate.split()) == 2):
                alpha1, number = carplate.split()[0], carplate.split()[1]
                # print("Two parts carplate", alpha1, number)
                # print("Alpha1 matches with", whitelist_check(alpha1, whitelist))
                carplate = carplate.replace(alpha1, whitelist_check(alpha1, whitelist))
                # print(any(el in carplate for el in whitelist))
                if any(ele in carplate for ele in blacklist) and any(el in carplate for el in whitelist) == False:
                        return "Invalid"
                return carplate
            elif (len(carplate.split()) == 3):
                alpha1, number, alpha2 = carplate.split()[0], carplate.split()[1], carplate.split()[2]
                # print("Three parts carplate", alpha1, number, alpha2)
                # print("Alpha1 matches with", whitelist_check(alpha1, whitelist))
                carplate = carplate.replace(alpha1, whitelist_check(alpha1, whitelist))
                carplate.replace(alpha1, whitelist_check(alpha1, whitelist))
                if any(ele in carplate
                    for ele in blacklist) and any(el in carplate
                                                    for el in whitelist) == False:
                    return "Invalid"
                return carplate
            else:
                return "Invalid"


        def whitelist_check(alpha, list):
            for x in list:
                if (similar(alpha, x) > 0.6):
                    alpha = x
            return alpha
        
        def possible_plate(carplate):
            lst = []
            checklist = ["W", "V", "B", "W", "8", "VV", "D", "0", "Q", "O", "0", "Q", "O", "Q"]
            changelist = ["VV", "W", "8", "V", "B", "W", "0", "D", "O", "Q", "Q", "0", "Q", "O"]
            #convert capital O into 0 and capital I into 1
            carplate = carplate.replace("O", "0")
            carplate = carplate.replace("I", "1")
            if(check(carplate) != "Invalid"):
                lst.append(standardise_string(carplate))
            carplate = list(carplate.replace(" ",""))
            #add the possible plate number into the list
            for i in range(len(carplate)):
                for j in range(len(checklist)):
                    if (carplate[i] == checklist[j]):
                        carplate[i] = changelist[j]
                        if(check("".join(carplate)) != "Invalid"):
                            lst.append(standardise_string("".join(carplate)))
            return lst


        def check(carplate):
            # print(carplate[0])
            if (carplate[0].isdigit()):
                return "Invalid"
            carplate = list(carplate.replace(" ",""))
            #adding space between aphla and numebrs
            for i in range(len(carplate) - 1):
                if ((carplate[i].isdigit() and carplate[i + 1].isalpha())
                    or (carplate[i + 1].isdigit() and carplate[i].isalpha())):
                    carplate[i] = carplate[i] + " "
            carplate = "".join(carplate).upper()
            #checking whether it start with a number
            if (len(carplate.split()) != 2 and len(carplate.split()) != 3):
                return "Invalid"
            elif len(carplate.split()[0]) > 3 or len(carplate[1].split())>4:
                return "Invalid"
            else:
                return carplate

        return list(set(possible_plate(carplate)))

    def clear_database(self):
        """Clear all records from the database."""
        try:
            sqliteConnection, cursor = self.create_connection()
            
            # Check if table exists first
            cursor.execute(f'''SELECT name FROM sqlite_master 
                             WHERE type='table' AND name='{self.parent_table}';''')
            if not cursor.fetchone():
                logger.info(f'Table {self.parent_table} does not exist, creating it')
                self.create_table()
                self.close_connection(sqliteConnection, cursor)
                return True
                
            # Delete all records
            delete_statement = f'DELETE FROM {self.parent_table}'
            cursor.execute(delete_statement)
            
            # Get number of deleted rows
            rows_deleted = cursor.rowcount
            logger.info(f'Database cleared successfully. {rows_deleted} rows deleted.')
            
            self.close_connection(sqliteConnection, cursor)
            return True
            
        except sqlite3.Error as error:
            logger.error(f'Error occurred while clearing database: {error}')
            return False