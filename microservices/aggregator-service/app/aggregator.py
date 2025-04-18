import warnings
import pandas as pd
import psycopg2, os
import mysql.connector
from decimal import Decimal
from dotenv import load_dotenv
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")
load_dotenv()

# === CONFIG ===
MYSQL_CONFIG = {
                'host': os.getenv('MYSQL_HOST'),
                'user': os.getenv('MYSQL_USER'), 
                'port': int(os.getenv('MYSQL_PORT', 3306)),
                'password': os.getenv('MYSQL_PASSWORD'),
                'database': os.getenv('MYSQL_DB')
                }

REDSHIFT_CONFIG = {
                'host': os.getenv('REDSHIFT_HOST'),
                'user': os.getenv('REDSHIFT_USER'),
                'port': int(os.getenv('REDSHIFT_PORT', 5439)),
                'password': os.getenv('REDSHIFT_PASSWORD'),
                'database': os.getenv('REDSHIFT_DB')
                }


YESTERDAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
YESTERDAY_PLUS_ONE = YESTERDAY + timedelta(days=1)
YESTERDAY_DATE = YESTERDAY.strftime("%Y-%m-%d %H:%M:%S")
YESTERDAY_PLUS_ONE_DATE = YESTERDAY_PLUS_ONE.strftime("%Y-%m-%d %H:%M:%S")

print(f"START WINDOW: {YESTERDAY}")
print(f"END WINDOW: {YESTERDAY_PLUS_ONE}")

# === DB HELPERS ===
def connect_mysql():
    return mysql.connector.connect(**MYSQL_CONFIG)

def connect_redshift():
    return psycopg2.connect(**REDSHIFT_CONFIG)

def execute_and_insert(source_cursor, dest_cursor, source_query, insert_query, table_name):    # 2. Run MySQL Query and insert fresh data into Redshift
    source_cursor.execute(source_query, (YESTERDAY_DATE, YESTERDAY_PLUS_ONE_DATE))
    rows = source_cursor.fetchall()
    if len(rows) > 0:
        dest_cursor.execute(
            f"DELETE FROM {table_name} WHERE aggregation_date::date = %s",
            (YESTERDAY_DATE,)
        )
        print(f"Deleted {len(rows)} rows from {table_name} for {YESTERDAY_DATE}")
        print(f"Added {len(rows)} rows to {table_name}\n")
        for row in rows:
            dest_cursor.execute(insert_query, (*row, YESTERDAY))


def run_etl():
    mysql_conn = connect_mysql()
    redshift_conn = connect_redshift()
    mysql_cur = mysql_conn.cursor()
    redshift_cur = redshift_conn.cursor()

    # 1. Best Performing Sales Teams (filter by sales.timestamp)
    execute_and_insert(
        mysql_cur, redshift_cur,
        """
        SELECT t.name AS team_name, SUM(s.sale_amount) AS total_sales
        FROM sales s
        JOIN teams t ON s.team_id = t.team_id
        WHERE s.timestamp >= %s AND s.timestamp < %s
        GROUP BY t.name
        ORDER BY total_sales DESC;
        """,
        """
        INSERT INTO redshift_team_performance(team_name, total_sales, aggregation_date)
        VALUES (%s, %s, %s);
        """,
        "redshift_team_performance"
    )

    # 2. Product Sales Target (filter by sales.timestamp)
    execute_and_insert(
        mysql_cur, redshift_cur,
        """
        SELECT p.name AS product_name,
               SUM(s.sale_amount) AS total_sales,
               CASE WHEN SUM(s.sale_amount) >= 3000000 THEN 'Achieved' ELSE 'Not Achieved' END AS status
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.timestamp >= %s AND s.timestamp < %s
        GROUP BY p.name
        ORDER BY total_sales DESC;
        """,
        """
        INSERT INTO redshift_product_performance(product_name, total_sales, status, aggregation_date)
        VALUES (%s, %s, %s, %s);
        """,
        "redshift_product_performance"
    )

    # 3. Branch Sales Performance (filter by sales.timestamp)
    execute_and_insert(
        mysql_cur, redshift_cur,
        """
        SELECT b.name AS branch_name, SUM(s.sale_amount) AS total_sales
        FROM sales s
        JOIN branches b ON s.branch_id = b.branch_id
        WHERE s.timestamp >= %s AND s.timestamp < %s
        GROUP BY b.name
        ORDER BY total_sales DESC;
        """,
        """
        INSERT INTO redshift_branch_performance(branch_name, total_sales, aggregation_date)
        VALUES (%s, %s, %s);
        """,
        "redshift_branch_performance"
    )

    # 4. Most Notified Agents (filter by notifications.created_at)
    execute_and_insert(
        mysql_cur, redshift_cur,
        """
        SELECT a.name AS agent_name, COUNT(n.notification_id) AS notification_count
        FROM notifications n
        JOIN agents a ON n.recipient_id = a.agent_id
        WHERE n.created_at >= %s AND n.created_at < %s
        GROUP BY a.name
        ORDER BY notification_count DESC;
        """,
        """
        INSERT INTO redshift_agent_notifications(agent_name, notification_count, aggregation_date)
        VALUES (%s, %s, %s);
        """,
        "redshift_agent_notifications"
    )

    # 5. Notification Summary by Status (filter by notifications.created_at)
    execute_and_insert(
        mysql_cur, redshift_cur,
        """
        SELECT status, COUNT(*) AS notification_count
        FROM notifications
        WHERE created_at >= %s AND created_at < %s
        GROUP BY status;
        """,
        """
        INSERT INTO redshift_notification_summary(status, notification_count, aggregation_date)
        VALUES (%s, %s, %s);
        """,
        "redshift_notification_summary"
    )

    # Finalize
    redshift_conn.commit()
    mysql_conn.close()
    redshift_conn.close()
    print(f"✅ ETL Complete — Insights written for: {YESTERDAY_DATE}")

if __name__ == "__main__":
    run_etl()