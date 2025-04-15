import os
from io import BytesIO
from PIL import Image

def get_image_dimensions(img_data):
    """
    Get the dimensions of an image from binary data
    
    Args:
        img_data (bytes): Binary image data
        
    Returns:
        tuple: (width, height) of the image
    """
    try:
        img = Image.open(BytesIO(img_data))
        return img.size
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return (0, 0)

def truncate_text(text, max_length=25):
    """
    Truncate text with ellipsis if it's too long
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length before truncation
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_price(price, currency="₽"):
    """
    Format a price with currency symbol
    
    Args:
        price (float): The price to format
        currency (str): Currency symbol
        
    Returns:
        str: Formatted price with currency
    """
    return f"{price:,.2f} {currency}"