import psycopg2


connection = psycopg2.connect(
    host="localhost",
    port=5433,
    database="defi_analytics",
    user="defi_user",
    password="defi_password",
)

cursor = connection.cursor()

cursor.execute("SELECT current_database(), version();")

database, version = cursor.fetchone()

print(f"Database: {database}")
print(f"PostgreSQL: {version}")

cursor.close()
connection.close()