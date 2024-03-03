import sqlite3
import pandas as pd
class SqlDatabase:

    def __init__(self, db_path):
        """
        :param db_path:
        """

        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def load_data_into_rsn_data(self, df):
        """
        :param df:
        :return:
        """
        # self.connection = sqlite3.connect(self.db_path)
        # Drop the existing table if it exists
        drop_table_query = f"DROP TABLE IF EXISTS rsn_data"
        self.cursor.execute(drop_table_query)
        self.connection.commit()

        df.to_sql("rsn_data", self.connection, index=False, if_exists='replace')

    def select_all_rsn_data(self):
        # Connect to the SQLite database

        # Execute a SQL query to select all data from the specified table
        query = f"SELECT * FROM rsn_data"
        df = pd.read_sql_query(query, self.connection)
        return df






