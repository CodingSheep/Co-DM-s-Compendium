import mysql.connector

from difflib import get_close_matches

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()
        # Connect to the SQL server
        try:
            self.connection = mysql.connector.connect(host=os.environ['SQL_HOST'],
                                                      database=os.environ['SQL_DB'],
                                                      user=os.environ['SQL_USER'],
                                                      password=os.environ['SQL_PASS'])
            self.cursor = self.connection.cursor()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            exit()

    def get_all_names(self, table):
        query = f"SELECT Name FROM {table}"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def search(self, name):
        results = {}

        # Queryable Tables
        tables = ["cities", "npcs", "locations"]

        # Get all names from each table to get close matches for querying
        all_names = {table: self.get_all_names(table) for table in tables}
        
        closest_matches = {}
        for table, names in all_names.items():
            match = get_close_matches(name, names, n=1, cutoff=0.6)
            if match:
                closest_matches[table] = match[0]
        
        # Determine which table to search based on the closest match
        if "cities" in closest_matches:
            city_query = "SELECT * FROM cities WHERE Name = %s"
            self.cursor.execute(query, (closest_matches["cities"],))
            city_rows = cursor.fetchall()

            if city_rows:
                results['cities'] = city_rows
                city_id = city_rows[0][0]

                district_query = "SELECT * FROM districts WHERE CityID = %s"
                self.cursor.execude(district_query, (city_id,))
                district_rows = self.cursor.fetchall()

                if district_rows:
                    results['districts'] = district_rows
        else:
            for table in ["npcs", "locations"]:
                if table in closest_matches:
                    query = f"SELECT * FROM {table} WHERE Name = %s"
                    self.cursor.execute(query, (closest_matches[table],))
                    rows = self.cursor.fetchall()
                    if rows:
                        results[table] = rows

        if results:
            return results
        return {"message": "No results found"}

    def save(self, table, object):
        try:
            # Parse data from JSON to valid SQL Insert
            columns = ', '.join(object.keys())
            placeholders = ', '.join(['%s'] * len(object))
            values = tuple(data.values())

            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.connection.commit()
            
            return True, _
        except Exception as e:
            return False, f"Error saving data to {table}: {e}"
        return