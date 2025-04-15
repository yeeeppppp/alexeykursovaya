import sqlite3
import os
import base64
from io import BytesIO
from PIL import Image

# Database file name
DB_FILE = "car_sales.db"

def get_connection():
    """
    Get a connection to the SQLite database
    
    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def setup_database():
    """
    Create the database and tables if they don't exist
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create cars table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        specifications TEXT NOT NULL,
        image BLOB
    )
    ''')
    
    # Create admin users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Insert test admin account if it doesn't exist
    cursor.execute("SELECT COUNT(*) FROM admins WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", 
                      ('admin', 'admin123'))
    
    conn.commit()
    conn.close()

def get_cars():
    """
    Get all cars from the database
    
    Returns:
        list: List of car dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, specifications, image FROM cars")
    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cars

def get_car(car_id):
    """
    Get a specific car by ID
    
    Args:
        car_id (int): Car ID
        
    Returns:
        dict: Car information or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, specifications, image FROM cars WHERE id = ?", (car_id,))
    car = cursor.fetchone()
    conn.close()
    
    if car:
        return dict(car)
    return None

def add_car(name, price, specifications, image_data):
    """
    Add a new car to the database
    
    Args:
        name (str): Car name
        price (float): Car price
        specifications (str): Car specifications
        image_data (bytes): Binary image data
        
    Returns:
        int: ID of the newly added car
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cars (name, price, specifications, image) VALUES (?, ?, ?, ?)",
        (name, price, specifications, image_data)
    )
    car_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return car_id

def delete_car(car_id):
    """
    Delete a car from the database
    
    Args:
        car_id (int): ID of the car to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def resize_image(image_data, width=800, height=600):
    """
    Resize image data to specified dimensions
    
    Args:
        image_data (bytes): Binary image data
        width (int): Target width
        height (int): Target height
        
    Returns:
        bytes: Resized image data
    """
    if not image_data:
        return None
        
    try:
        # Open the image from binary data
        img = Image.open(BytesIO(image_data))
        
        # Resize the image
        img = img.resize((width, height), Image.LANCZOS)
        
        # Save the resized image to a BytesIO object
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        
        # Return the binary data
        return output.getvalue()
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None
