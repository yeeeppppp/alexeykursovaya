import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from io import BytesIO

def center_window(window, width, height):
    """
    Center a tkinter window on the screen
    
    Args:
        window: Tkinter window object
        width (int): Window width
        height (int): Window height
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def load_image_file():
    """
    Open a file dialog to select an image file
    
    Returns:
        tuple: (image_data, tk_image) or (None, None) if cancelled
    """
    file_types = [
        ('Image files', '*.jpg;*.jpeg;*.png;*.gif'),
        ('All files', '*.*')
    ]
    
    file_path = filedialog.askopenfilename(filetypes=file_types)
    if not file_path:
        return None, None
    
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        # Create TkInter compatible image
        image = Image.open(BytesIO(image_data))
        image = image.resize((150, 100), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(image)
        
        return image_data, tk_image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

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