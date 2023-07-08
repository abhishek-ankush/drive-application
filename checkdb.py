host = 'database-1.ck5jcmrtfsnq.ap-south-1.rds.amazonaws.com'
port = 3306  # Default port for MySQL
user = 'admin'
password = 'JrNyxMhtCswVSajn5wUo'
database = 'driveapp'

import mysql.connector

def create_file_table():
    try:
        # Connect to the Amazon RDS database
        db_connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        cursor = db_connection.cursor()

        # Create the 'file' table if it doesn't exist
        create_table_query = """
            CREATE TABLE IF NOT EXISTS file_test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255),
                upload_date DATETIME
            )
        """
        cursor.execute(create_table_query)

        cursor.close()
        db_connection.close()

        print("File table created successfully.")
    except Exception as e:
        print("Error creating file table:", e)

# Call the function to create the 'file' table
create_file_table()