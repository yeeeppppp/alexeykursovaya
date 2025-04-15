import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import re
from io import BytesIO
from PIL import Image, ImageTk

from database import setup_database, get_cars, get_car, add_car, delete_car, get_image_from_data
from auth import login
from utils import center_window, load_image_file, truncate_text

class CarSalesApp:
    """Main application class managing all UI frames"""
    
    def __init__(self, root):
        """
        Initialize the application
        
        Args:
            root: Tkinter root window
        """
        # Ensure database is set up
        setup_database()
        
        self.root = root
        self.root.title("Приложение продажи автомобилей")
        self.root.minsize(800, 600)
        
        center_window(root, 1000, 700)
        
        self.frames = {}
        
        # Configure style
        self.setup_styles()
        
        # Конфигурируем цвета канваса - используем тот же цвет, что и в стилях
        self.list_canvas_bg = "#f5f5f5"  # Светло-серый фон
        
        # Create container for frames
        container = ttk.Frame(root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Store image references to prevent garbage collection
        self.image_references = []
        
        # Create a dictionary of frames
        for F in (RoleSelectionFrame, UserFrame, AdminLoginFrame, AdminDashboardFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show initial frame
        self.show_frame(RoleSelectionFrame)

    def setup_styles(self):
        """Setup ttk styles for the application"""
        style = ttk.Style()
        
        # Основные цвета приложения
        main_bg = "#f5f5f5"         # Светло-серый фон - тот же цвет, что и list_canvas_bg
        accent_color = "#3498db"     # Синий акцент
        secondary_color = "#e74c3c"  # Красный для кнопок удаления
        success_color = "#2ecc71"    # Зеленый для цены
        text_color = "#2c3e50"       # Темно-синий для текста
        card_bg = "#ffffff"          # Белый фон карточек
        card_hover = "#ebf5fb"       # Светло-голубой при наведении
        
        # Настройка основного фона
        style.configure(".", background=main_bg, foreground=text_color)
        
        # Configure TLabel style
        style.configure("TLabel", font=("Arial", 11), background=main_bg, foreground=text_color)
        
        # Явно настраиваем цвет фона и текста для всех виджетов
        style.configure("TFrame", background=main_bg)
        style.configure("TEntry", fieldbackground="white", foreground=text_color)
        style.configure("TNotebook", background=main_bg)
        style.configure("TNotebook.Tab", background=main_bg, foreground=text_color, padding=[10, 5])
        
        # Настраиваем цвета для Treeview (таблицы)
        style.configure("Treeview", 
                       background="white", 
                       foreground=text_color,
                       fieldbackground="white")
        style.configure("Treeview.Heading", 
                       background=main_bg,
                       foreground=text_color,
                       font=("Arial", 10, "bold"))
        style.map("Treeview", 
                background=[("selected", accent_color)],
                foreground=[("selected", "white")])
        
        # Configure TButton style
        style.configure("TButton", 
                       font=("Arial", 11, "bold"), 
                       padding=5,
                       background=accent_color,
                       foreground="black")
        
        # Configure Delete button style
        style.configure("Delete.TButton", 
                       background=secondary_color,
                       foreground="black")
        
        # Configure success button style
        style.configure("Success.TButton", 
                       background=success_color,
                       foreground="black")
        
        # Configure large TButton style for role selection
        style.configure("Large.TButton", 
                       font=("Arial", 12, "bold"), 
                       padding=10,
                       background=accent_color,
                       foreground="black")
        
        # Configure Admin.TButton style
        style.configure("Admin.TButton", 
                       background=secondary_color,
                       foreground="black")
        
        # TFrame уже настроен выше
        
        # Configure Card.TFrame style for car cards
        style.configure("Card.TFrame", background=card_bg, relief="flat", borderwidth=1)
        style.map("Card.TFrame",
                 background=[("active", card_hover)],
                 relief=[("active", "raised")])
        
        # Configure Header.TLabel style
        style.configure("Header.TLabel", 
                       font=("Arial", 16, "bold"), 
                       background=main_bg, 
                       foreground=text_color)
        
        # Configure Title.TLabel style
        style.configure("Title.TLabel", 
                       font=("Arial", 24, "bold"), 
                       background=main_bg, 
                       foreground=accent_color)
        
        # Configure Subtitle.TLabel style
        style.configure("Subtitle.TLabel", 
                       font=("Arial", 14, "bold"), 
                       background=main_bg, 
                       foreground=text_color)
        
        # Configure Card label styles
        style.configure("Card.TLabel", background=card_bg)
        style.configure("CardTitle.TLabel", 
                       font=("Arial", 18, "bold"), 
                       background=card_bg, 
                       foreground=text_color)

        # Configure Price.TLabel style
        style.configure("Price.TLabel", 
                       font=("Arial", 16, "bold"), 
                       background=card_bg, 
                       foreground=success_color)
                       
        # Конфигурация стиля для выделенных карточек
        style.configure("Selected.Card.TFrame", 
                      background="#d6eaf8",  # Светло-синий фон для выделенной карточки
                      relief="raised", 
                      borderwidth=2)
        
    def show_frame(self, frame_class):
        """
        Bring a frame to the front and update it if needed
        
        Args:
            frame_class: The class of the frame to show
        """
        frame = self.frames[frame_class]
        frame.tkraise()
        
        # If the frame has an update method, call it
        if hasattr(frame, 'update_frame'):
            frame.update_frame()
    
    def add_image_ref(self, img):
        """
        Add an image reference to prevent garbage collection
        
        Args:
            img: Image reference to keep
        """
        self.image_references.append(img)

class RoleSelectionFrame(ttk.Frame):
    """Frame for role selection"""
    
    def __init__(self, parent, controller):
        """
        Initialize the role selection frame
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=50)
        
        ttk.Label(
            header_frame, 
            text="Добро пожаловать в приложение продажи автомобилей", 
            style="Title.TLabel"
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Выберите, как вы хотите продолжить:",
            style="Subtitle.TLabel"
        ).pack(pady=10)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(expand=True)
        
        # Create role buttons with space in between
        user_button = ttk.Button(
            buttons_frame,
            text="Продолжить как покупатель",
            style="Large.TButton",
            command=lambda: controller.show_frame(UserFrame)
        )
        user_button.grid(row=0, column=0, padx=20, pady=20)
        
        admin_button = ttk.Button(
            buttons_frame,
            text="Войти как администратор",
            style="Admin.TButton",
            command=lambda: controller.show_frame(AdminLoginFrame)
        )
        admin_button.grid(row=0, column=1, padx=20, pady=20)

class UserFrame(ttk.Frame):
    """Frame for user view (car list and details)"""
    
    def __init__(self, parent, controller):
        """
        Initialize the user frame
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Store selected car id
        self.selected_car_id = None
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(
            header_frame, 
            text="Каталог автомобилей", 
            style="Header.TLabel"
        ).pack(side="left")
        
        ttk.Button(
            header_frame,
            text="Вернуться к выбору роли",
            style="TButton",
            command=lambda: controller.show_frame(RoleSelectionFrame)
        ).pack(side="right")
        
        # Создаем стек-фреймы (один поверх другого) для списка и деталей
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Создаем фрейм для списка (на весь экран)
        self.list_frame = ttk.Frame(self.content_frame)
        self.list_frame.pack(fill="both", expand=True)
        
        # Создаем фрейм для деталей (на весь экран, изначально скрыт)
        self.detail_frame = ttk.Frame(self.content_frame)
        
        # Настраиваем фреймы
        self.setup_list_frame()
        self.setup_detail_frame()
        
        # Изначально показываем список автомобилей
        self.list_frame.pack(fill="both", expand=True)
        self.detail_frame.pack_forget()
    
    def setup_list_frame(self):
        """Setup the car list frame with header and scrollable list"""
        # Используем прямой фрейм без Canvas и scrollbar
        self.car_list_container = ttk.Frame(self.list_frame)
        self.car_list_container.pack(fill="both", expand=True)
        
        # Создаем контейнер для элементов с прокруткой
        self.list_canvas_frame = ttk.Frame(self.car_list_container)
        self.list_canvas_frame.pack(fill="both", expand=True)
        
        # Create a Canvas with a scrollbar
        self.list_canvas = tk.Canvas(self.list_canvas_frame, bg=self.controller.list_canvas_bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.list_canvas_frame, orient="vertical", command=self.list_canvas.yview)
        
        # Pack the scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.list_canvas.pack(side="left", fill="both", expand=True)
        
        # Create a frame inside the canvas for car items
        self.car_items_frame = ttk.Frame(self.list_canvas, style="TFrame")
        self.canvas_window = self.list_canvas.create_window((0, 0), window=self.car_items_frame, anchor="nw")
        
        # Connect scrollbar to canvas
        self.list_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Update scrollregion when the size of the frame changes
        self.car_items_frame.bind("<Configure>", self.on_frame_configure)
        
        # Bind mousewheel to scroll
        self.list_canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.list_canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.list_canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down
        
    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        
    def on_mousewheel(self, event):
        """Scroll the canvas on mousewheel events"""
        if event.num == 4 or event.delta > 0:  # Scroll up
            self.list_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # Scroll down
            self.list_canvas.yview_scroll(1, "units")
    
    def setup_detail_frame(self):
        """Setup the car detail frame with placeholders"""
        # Детальный фрейм будет создаваться динамически для каждого автомобиля
        pass
    
    def update_frame(self):
        """Update the car list when the frame is shown"""
        # Очищаем список автомобилей и создаем заново контейнер
        self.setup_list_frame()
        
        # Get cars from database
        cars = get_cars()
        
        if not cars:
            ttk.Label(
                self.car_items_frame, 
                text="Нет доступных автомобилей", 
                style="Subtitle.TLabel"
            ).pack(pady=20)
            return
        
        # Add each car to the list
        self.car_frames = []  # Сохраняем ссылки на все карточки
        
        for i, car in enumerate(cars):
            # Создаем карточку автомобиля
            car_frame = ttk.Frame(self.car_items_frame, style="Card.TFrame")
            car_frame.pack(fill="x", padx=20, pady=10, ipadx=10, ipady=10)
            
            # Сохраняем id автомобиля как атрибут
            setattr(car_frame, 'car_id', car['id'])
            self.car_frames.append(car_frame)
            
            # Добавляем эффекты при наведении
            for widget in [car_frame]:
                widget.bind("<Enter>", lambda e, cf=car_frame: self.on_car_hover(cf, True))
                widget.bind("<Leave>", lambda e, cf=car_frame: self.on_car_hover(cf, False))
                
                # Добавляем обработчик клика
                widget.bind("<Button-1>", self.on_car_click)
            
            # Контейнер для контента карточки
            car_content = ttk.Frame(car_frame, style="Card.TFrame")
            car_content.pack(fill="both", expand=True)
            
            # Добавляем событие клика для всех дочерних элементов
            car_content.bind("<Button-1>", self.on_car_click)
            
            # Добавляем изображение автомобиля
            image_frame = ttk.Frame(car_content, width=220, height=150, style="Card.TFrame")
            image_frame.pack(side="left", padx=15, pady=10)
            image_frame.pack_propagate(False)
            setattr(image_frame, 'car_id', car['id'])  # Привязываем id к каждому элементу
            image_frame.bind("<Button-1>", self.on_car_click)
            
            image_label = ttk.Label(image_frame, style="Card.TLabel")
            image_label.pack(fill="both", expand=True)
            setattr(image_label, 'car_id', car['id'])
            image_label.bind("<Button-1>", self.on_car_click)
            
            if car['image']:
                photo = get_image_from_data(car['image'])
                if photo:
                    image_label.config(image=photo)
                    self.controller.add_image_ref(photo)
            
            # Добавляем детали автомобиля
            details_frame = ttk.Frame(car_content, style="Card.TFrame")
            details_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
            setattr(details_frame, 'car_id', car['id'])
            details_frame.bind("<Button-1>", self.on_car_click)
            
            name_label = ttk.Label(
                details_frame, 
                text=car['name'], 
                style="CardTitle.TLabel"
            )
            name_label.pack(anchor="w")
            setattr(name_label, 'car_id', car['id'])
            name_label.bind("<Button-1>", self.on_car_click)
            
            price_label = ttk.Label(
                details_frame, 
                text=f"₽{car['price']:.2f}", 
                style="Price.TLabel"
            )
            price_label.pack(anchor="w", pady=10)
            setattr(price_label, 'car_id', car['id'])
            price_label.bind("<Button-1>", self.on_car_click)
            
    def on_car_click(self, event):
        """Обработчик клика по элементу карточки автомобиля"""
        # Получаем id автомобиля из свойства виджета
        widget = event.widget
        car_id = getattr(widget, 'car_id', None)
        
        # Если у виджета нет свойства car_id, ищем родительский элемент
        if car_id is None:
            parent = widget.master
            car_id = getattr(parent, 'car_id', None)
        
        # Если нашли id, показываем детали
        if car_id:
            self.show_car_detail(car_id)
    
    def on_car_hover(self, frame, is_hover):
        """
        Highlight car item on hover
        
        Args:
            frame: Frame to highlight
            is_hover (bool): Whether mouse is over the item
        """
        if is_hover:
            frame.configure(style="Card.TFrame")
            frame['relief'] = 'raised'
        else:
            frame.configure(style="Card.TFrame")
            frame['relief'] = 'flat'
    
    def show_car_detail(self, car_id):
        """
        Show details for a selected car
        
        Args:
            car_id (int): ID of the car to display
        """
        # Store selected car id
        self.selected_car_id = car_id
        
        # Get car details
        car = get_car(car_id)
        if not car:
            messagebox.showerror("Ошибка", "Автомобиль не найден")
            return
        
        # Очищаем предыдущие виджеты, если они существуют
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        # Создаем верхнюю панель с заголовком и кнопкой назад
        header_frame = ttk.Frame(self.detail_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(
            header_frame, 
            text=car['name'], 
            style="Header.TLabel",
            font=("Arial", 22, "bold")
        ).pack(side="left")
        
        ttk.Button(
            header_frame,
            text="Вернуться к списку",
            style="TButton",
            command=self.show_car_list
        ).pack(side="right")
        
        # Создаем основной контейнер с контентом
        content_frame = ttk.Frame(self.detail_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Добавляем изображение
        image_frame = ttk.Frame(content_frame)
        image_frame.pack(pady=20)
        
        image_label = ttk.Label(image_frame)
        image_label.pack()
        
        if car['image']:
            # Create a larger version of the image for detail view
            image = Image.open(BytesIO(car['image']))
            image = image.resize((400, 300), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_label.config(image=photo)
            self.controller.add_image_ref(photo)
        
        # Добавляем цену
        price_frame = ttk.Frame(content_frame)
        price_frame.pack(fill="x", pady=10)
        
        ttk.Label(
            price_frame, 
            text=f"Цена: ₽{car['price']:.2f}", 
            style="Price.TLabel",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")
        
        # Добавляем характеристики
        specs_frame = ttk.Frame(content_frame)
        specs_frame.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(
            specs_frame, 
            text="Характеристики:", 
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(0, 5))
        
        specs_text = tk.Text(specs_frame, height=15, width=50, 
                           bg="white", fg="#2c3e50")
        specs_text.pack(fill="both", expand=True)
        
        # Заполняем характеристики
        specs_text.insert(tk.END, car['specifications'])
        specs_text.config(state="disabled")
        
        # Показываем детальный фрейм и скрываем список
        self.list_frame.pack_forget()
        self.detail_frame.pack(fill="both", expand=True)
        
    def show_car_list(self):
        """Возвращаемся к списку автомобилей"""
        # Показываем список и скрываем детали
        self.detail_frame.pack_forget()
        self.list_frame.pack(fill="both", expand=True)

class AdminLoginFrame(ttk.Frame):
    """Frame for admin login"""
    
    def __init__(self, parent, controller):
        """
        Initialize the admin login frame
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Create content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(expand=True)
        
        # Login form header
        ttk.Label(
            content_frame, 
            text="Вход для администратора", 
            style="Header.TLabel"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Username field
        ttk.Label(
            content_frame, 
            text="Имя пользователя:"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        
        self.username_var = tk.StringVar()
        ttk.Entry(
            content_frame, 
            textvariable=self.username_var,
            width=30
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Password field
        ttk.Label(
            content_frame, 
            text="Пароль:"
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        
        self.password_var = tk.StringVar()
        ttk.Entry(
            content_frame, 
            textvariable=self.password_var,
            show="*",
            width=30
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Error label
        self.error_label = ttk.Label(
            content_frame, 
            text="",
            foreground="red"
        )
        self.error_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Buttons
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="Войти",
            style="Success.TButton",
            command=self.login
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Назад",
            style="TButton",
            command=lambda: controller.show_frame(RoleSelectionFrame)
        ).grid(row=0, column=1, padx=5)
    
    def login(self):
        """Handle admin login"""
        username = self.username_var.get()
        password = self.password_var.get()
        
        if login(username, password):
            # Clear error and form
            self.error_label.config(text="")
            self.username_var.set("")
            self.password_var.set("")
            
            # Show admin dashboard
            self.controller.show_frame(AdminDashboardFrame)
        else:
            self.error_label.config(text="Неверное имя пользователя или пароль")

class AdminDashboardFrame(ttk.Frame):
    """Frame for admin dashboard"""
    
    def __init__(self, parent, controller):
        """
        Initialize the admin dashboard frame
        
        Args:
            parent: Parent widget
            controller: Application controller
        """
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Store image for adding cars
        self.new_car_image_data = None
        self.new_car_image_preview = None
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(
            header_frame, 
            text="Панель администратора", 
            style="Header.TLabel"
        ).pack(side="left")
        
        ttk.Button(
            header_frame,
            text="Выйти",
            style="TButton",
            command=lambda: controller.show_frame(RoleSelectionFrame)
        ).pack(side="right")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.list_tab = ttk.Frame(self.notebook)
        self.add_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.list_tab, text="Список автомобилей")
        self.notebook.add(self.add_tab, text="Добавить автомобиль")
        
        # Setup each tab
        self.setup_list_tab()
        self.setup_add_tab()
    
    def setup_list_tab(self):
        """Setup the car list tab with table and delete functionality"""
        # Create treeview for cars list
        columns = ("id", "name", "price", "specs")
        self.car_tree = ttk.Treeview(self.list_tab, columns=columns, show="headings")
        
        # Setup columns
        self.car_tree.heading("id", text="ID")
        self.car_tree.heading("name", text="Название")
        self.car_tree.heading("price", text="Цена (₽)")
        self.car_tree.heading("specs", text="Характеристики")
        
        # Set column widths
        self.car_tree.column("id", width=50)
        self.car_tree.column("name", width=200)
        self.car_tree.column("price", width=100)
        self.car_tree.column("specs", width=400)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.list_tab, orient="vertical", command=self.car_tree.yview)
        self.car_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.car_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add button frame below
        button_frame = ttk.Frame(self.list_tab)
        button_frame.pack(pady=10, fill="x")
        
        # Add delete button
        ttk.Button(
            button_frame,
            text="Удалить выбранный автомобиль",
            style="Delete.TButton",
            command=self.delete_selected_car
        ).pack(side="right")
    
    def setup_add_tab(self):
        """Setup the add car tab with form fields"""
        # Create form frame
        form_frame = ttk.Frame(self.add_tab)
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Car name
        ttk.Label(
            form_frame, 
            text="Название автомобиля:"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.car_name_var = tk.StringVar()
        ttk.Entry(
            form_frame, 
            textvariable=self.car_name_var,
            width=50
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Car price
        ttk.Label(
            form_frame, 
            text="Цена (₽):"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.car_price_var = tk.StringVar()
        ttk.Entry(
            form_frame, 
            textvariable=self.car_price_var,
            width=20
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Car specifications
        ttk.Label(
            form_frame, 
            text="Характеристики:",
            style="Subtitle.TLabel"
        ).grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        
        self.specs_text = tk.Text(form_frame, height=10, width=50, 
                                bg="white", fg="#2c3e50")
        self.specs_text.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Car image
        ttk.Label(
            form_frame, 
            text="Изображение:"
        ).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        image_frame = ttk.Frame(form_frame)
        image_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Button(
            image_frame,
            text="Выбрать изображение",
            style="TButton",
            command=self.select_image
        ).pack(side="left", padx=(0, 10))
        
        self.image_label = ttk.Label(image_frame, text="Нет выбранного изображения")
        self.image_label.pack(side="left")
        
        # Image preview
        self.preview_label = ttk.Label(form_frame)
        self.preview_label.grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        
        # Submit button
        ttk.Button(
            form_frame,
            text="Добавить автомобиль",
            style="Success.TButton",
            command=self.add_car
        ).grid(row=5, column=0, columnspan=2, pady=20)
    
    def update_frame(self):
        """Update the car list when the frame is shown"""
        # Clear existing car list
        for item in self.car_tree.get_children():
            self.car_tree.delete(item)
        
        # Get cars from database
        cars = get_cars()
        
        # Add each car to the treeview
        for car in cars:
            # Truncate specifications for display
            short_specs = truncate_text(car['specifications'], 100)
            
            self.car_tree.insert("", "end", values=(
                car['id'], 
                car['name'], 
                f"{car['price']:.2f}", 
                short_specs
            ))
    
    def select_image(self):
        """Open file dialog to select an image for the new car"""
        image_data, tk_image = load_image_file()
        if image_data and tk_image:
            self.new_car_image_data = image_data
            self.new_car_image_preview = tk_image
            self.image_label.config(text="Изображение выбрано")
            self.preview_label.config(image=self.new_car_image_preview)
            self.controller.add_image_ref(self.new_car_image_preview)
        else:
            self.image_label.config(text="Нет выбранного изображения")
    
    def add_car(self):
        """Add a new car with form data"""
        try:
            # Get form data
            name = self.car_name_var.get().strip()
            price_str = self.car_price_var.get().strip()
            specifications = self.specs_text.get("1.0", tk.END).strip()
            
            # Validate inputs
            if not name:
                messagebox.showerror("Ошибка", "Пожалуйста, введите название автомобиля")
                return
            
            if not price_str:
                messagebox.showerror("Ошибка", "Пожалуйста, введите цену автомобиля")
                return
            
            # Validate price format
            if not re.match(r'^\d+(\.\d{1,2})?$', price_str):
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректную цену (например: 1000000 или 1000000.00)")
                return
            
            price = float(price_str)
            
            if not specifications:
                messagebox.showerror("Ошибка", "Пожалуйста, введите характеристики автомобиля")
                return
            
            # Add car to database
            car_id = add_car(name, price, specifications, self.new_car_image_data)
            
            if car_id:
                messagebox.showinfo("Успех", "Автомобиль успешно добавлен")
                
                # Clear form
                self.car_name_var.set("")
                self.car_price_var.set("")
                self.specs_text.delete("1.0", tk.END)
                self.new_car_image_data = None
                self.image_label.config(text="Нет выбранного изображения")
                self.preview_label.config(image="")
                
                # Update car list
                self.update_frame()
                
                # Switch to list tab
                self.notebook.select(0)
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить автомобиль")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    
    def delete_selected_car(self):
        """Delete the currently selected car"""
        selected_item = self.car_tree.selection()
        if not selected_item:
            messagebox.showinfo("Информация", "Пожалуйста, выберите автомобиль для удаления")
            return
        
        # Get car id from selected item
        car_id = self.car_tree.item(selected_item[0])['values'][0]
        
        # Ask for confirmation
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранный автомобиль?"):
            success = delete_car(car_id)
            
            if success:
                messagebox.showinfo("Успех", "Автомобиль успешно удален")
                self.update_frame()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить автомобиль")