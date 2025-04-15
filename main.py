import tkinter as tk
from ui import CarSalesApp

def main():
    """
    Main entry point of the application
    """
    # Создаем корневое окно Tkinter
    root = tk.Tk()
    
    # Инициализируем приложение
    app = CarSalesApp(root)
    
    # Запускаем главный цикл приложения
    print("Приложение успешно запущено. Для завершения работы закройте окно приложения.")
    root.mainloop()

if __name__ == "__main__":
    main()