import sqlite3
from database import get_connection

def login(username, password):
    """
    Verify admin login credentials
    
    Args:
        username (str): Admin username
        password (str): Admin password
        
    Returns:
        bool: True if login is successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM admins WHERE username = ? AND password = ?",
        (username, password)
    )
    admin = cursor.fetchone()
    conn.close()
    
    return admin is not None