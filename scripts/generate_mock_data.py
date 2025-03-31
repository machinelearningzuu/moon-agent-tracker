import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_config = {
            'host': os.getenv('MYSQL_HOST'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DB')
            }

def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def read_csv_data():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Read all CSV files
    agents_df = pd.read_csv(os.path.join(data_dir, 'agents.csv'))
    branches_df = pd.read_csv(os.path.join(data_dir, 'branches.csv'))
    products_df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
    sales_df = pd.read_csv(os.path.join(data_dir, 'sales.csv'))
    teams_df = pd.read_csv(os.path.join(data_dir, 'teams.csv'))
    
    return {
        'agents': agents_df,
        'branches': branches_df,
        'products': products_df,
        'sales': sales_df,
        'teams': teams_df
    }

def insert_data(connection, data):
    cursor = connection.cursor()
    
    # Create tables if they don't exist
    create_tables_queries = {
        'branches': """
        CREATE TABLE IF NOT EXISTS branches (
            branch_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100),
            location VARCHAR(100)
        )
        """,
        'teams': """
        CREATE TABLE IF NOT EXISTS teams (
            team_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100),
            branch_id VARCHAR(10),
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
        )
        """,
        'products': """
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(50),
            commission_percentage DECIMAL(5,2),
            status VARCHAR(20)
        )
        """,
        'agents': """
        CREATE TABLE IF NOT EXISTS agents (
            agent_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(20),
            branch_id VARCHAR(10),
            team_id VARCHAR(10),
            products_allowed TEXT,
            status VARCHAR(20),
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
        """,
        'sales': """
        CREATE TABLE IF NOT EXISTS sales (
            sale_id VARCHAR(10) PRIMARY KEY,
            agent_id VARCHAR(10),
            product_id VARCHAR(10),
            sale_amount DECIMAL(10,2),
            timestamp DATETIME,
            branch_id VARCHAR(10),
            team_id VARCHAR(10),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
        """
    }
    
    # Create tables
    for table_name, query in create_tables_queries.items():
        cursor.execute(query)
    
    # Define the order of table insertion based on dependencies
    table_order = ['branches', 'teams', 'products', 'agents', 'sales']
    
    # Insert data from each DataFrame in the correct order
    for table_name in table_order:
        print(f"Checking and inserting data into {table_name} table")
        
        # Check if table is empty
        check_query = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(check_query)
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Table is empty, insert all data
            df = data[table_name]
            for _, row in df.iterrows():
                columns = ', '.join(row.index)
                placeholders = ', '.join(['%s'] * len(row))
                insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                try:
                    cursor.execute(insert_query, tuple(row))
                except mysql.connector.Error as err:
                    print(f"Error inserting row into {table_name}: {err}")
                    print(f"Row data: {row}")
            print(f"Inserted {len(df)} records into {table_name}")
        else:
            print(f"Table {table_name} already contains data, skipping insertion")
    
    connection.commit()
    cursor.close()

def main():
    # Connect to database
    connection = connect_to_database()
    if not connection:
        return
    
    try:
        # Read data from CSV files
        data = read_csv_data()
        
        # Insert data into database
        insert_data(connection, data)
        print("Successfully inserted data from CSV files into the database!")
        
    except Exception as err:
        print(f"Error: {err}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()