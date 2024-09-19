import sqlite3
from tabulate import tabulate

class RaceGrades:
    def __init__(self, race_class, distance):
        self.overlay_rank = self.calculate_overlay_rank(race_class, distance)
        self.price_rank = self.calculate_price_rank(race_class, distance)
        self.fraud_by_class_grade = self.calculate_fraud_class(race_class, distance)




    def __repr__(self):
        table_data = [
            ["Overlay Rank", self.overlay_rank],
            ["Price Rank", self.price_rank],
            ["Fraud Grade", self.fraud_by_class_grade]

        ]
        table_str = tabulate(table_data, headers=["Attribute", "Rank"], tablefmt="fancy_grid")

        # Encode the table string using UTF-8 to handle non-ASCII characters
        return table_str.encode('utf-8')

    @classmethod
    def calculate_overlay_rank(cls, race_class, distance):
        # Connect to the SQLite database
        conn = sqlite3.connect('nov15.db')
        cursor = conn.cursor()

        # Execute the SQL query
        query = """
        SELECT AVG(overlay) AS avg_overlay, COUNT(class) AS class_count, class
        FROM races
        WHERE overlay_bool = 'True' AND won_race = 'True'
        GROUP BY class
        HAVING COUNT(class) >= 50
        ORDER BY avg_overlay DESC;
        """
        cursor.execute(query)

        # Fetch all the results
        results = cursor.fetchall()

        # Close the connection
        conn.close()

        # Calculate rank using a separate function
        rank = cls.find_rank(race_class, results)
        return rank


    @classmethod
    def calculate_price_rank(cls, race_class, distance):
        # Connect to the SQLite database
        conn = sqlite3.connect('nov15.db')
        cursor = conn.cursor()

        # Execute the SQL query
        query = """
        SELECT AVG(price) AS avg_overlay, COUNT(class) AS class_count, class
        FROM races
        WHERE won_race = 'True'
        GROUP BY class
        HAVING COUNT(class) >= 50
        ORDER BY price DESC;
        """
        cursor.execute(query)

        # Fetch all the results
        results = cursor.fetchall()

        # Close the connection
        conn.close()

        # Calculate rank using a separate function
        rank = cls.find_rank(race_class, results)
        return rank


    @classmethod
    def calculate_fraud_class(cls, race_class, distance):
        # Connect to the SQLite database
        conn = sqlite3.connect('nov15.db')
        cursor = conn.cursor()

        # Execute the SQL query
        query = """
        SELECT

            COUNT(*) AS total_false_won_race,
            (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM races WHERE ml_odds < 2.5 AND won_race = 'False') AS percentage_false_won_race,
            class
        FROM races
        WHERE ml_odds < 2.5 AND won_race = 'False'
        GROUP BY class having count(class) >= 50
        ORDER BY percentage_false_won_race DESC;
        """
        cursor.execute(query)

        # Fetch all the results
        results = cursor.fetchall()

        # Close the connection
        conn.close()

        # Calculate rank using a separate function
        rank = cls.find_rank(race_class, results)
        return rank

    @staticmethod
    def find_rank(class_name, results):
        num_classes = len(results)
        top_third_cutoff = num_classes // 3
        middle_third_cutoff = top_third_cutoff * 2

        for rank, (_, _, cls1) in enumerate(results, start=1):
            if cls1 == class_name:
                if rank <= top_third_cutoff:
                    return 'A'
                elif rank <= middle_third_cutoff:
                    return 'B'
                else:
                    return 'C'
        return 'N/A'  # Class not found in results