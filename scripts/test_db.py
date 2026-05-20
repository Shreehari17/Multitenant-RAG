from core.db import get_connection, release_connection

def test_connection():
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT VERSION();")
        version=cursor.fetchone()
        print("Connection successful")
        print(f"Postgres version is {version[0]}")
        cursor.close()
        conn.close()
        print("Connection closed")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
    