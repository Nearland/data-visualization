import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import datatest  

MARKER_STYLE = 'H'  # Шестиугольник
DEFAULT_COLOR = 'steelblue'

class ScatterPlotApp:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.root.title("Scatter Plot Tool - Задание 2")
        
        # Получаем список числовых колонок
        self.numeric_cols = ['order_quantity', 'sales', 'discount', 'discount_value']
        # Проверяем, какие из них есть в датасете
        self.numeric_cols = [col for col in self.numeric_cols if col in df.columns]
        
        if len(self.numeric_cols) < 2:
            print("Ошибка: недостаточно числовых колонок для построения графика")
            self.root.destroy()
            return
        
        # Переменные для выбранных колонок
        self.x_var = tk.StringVar(value=self.numeric_cols[0])
        self.y_var = tk.StringVar(value=self.numeric_cols[1])
        
        # Создаём интерфейс
        self.setup_ui()
        
        # Строим начальный график
        self.update_plot()
    
    def setup_ui(self):
        # Основной фрейм для размещения
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Фрейм для кнопок выбора осей (слева от графика)
        left_frame = ttk.LabelFrame(main_frame, text="Выбор оси X", padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Фрейм для графика (по центру)
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Фрейм для кнопок выбора осей (снизу от графика)
        bottom_frame = ttk.LabelFrame(main_frame, text="Выбор оси Y", padding="5")
        bottom_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Создаём фигуру matplotlib
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Кнопки для оси X (вертикальный список слева)
        for col in self.numeric_cols:
            btn = ttk.Button(left_frame, text=col, width=20,
                            command=lambda c=col: self.set_x_column(c))
            btn.pack(pady=2)
        
        # Кнопки для оси Y (горизонтальный список снизу)
        for col in self.numeric_cols:
            btn = ttk.Button(bottom_frame, text=col,
                            command=lambda c=col: self.set_y_column(c))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Кнопка сохранения (внизу слева)
        save_btn = ttk.Button(main_frame, text="Сохранить график", command=self.save_plot)
        save_btn.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
    
    def set_x_column(self, col):
        self.x_var.set(col)
        self.update_plot()
    
    def set_y_column(self, col):
        self.y_var.set(col)
        self.update_plot()
    
    def update_plot(self):
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        
        # Очищаем оси
        self.ax.clear()
        
        # Получаем данные
        valid_data = self.df[[x_col, y_col]].dropna()
        x_data = valid_data[x_col]
        y_data = valid_data[y_col]
        
        # Строим точечную диаграмму с маркером-шестиугольником
        self.ax.scatter(x_data, y_data, alpha=0.6, s=30, 
                       marker=MARKER_STYLE, color=DEFAULT_COLOR)
        
        # Подписи осей
        self.ax.set_xlabel(x_col, fontsize=10)
        self.ax.set_ylabel(y_col, fontsize=10)
        self.ax.set_title(f'Scatter Plot: {x_col} vs {y_col}', fontsize=12)
        
        # Сетка для удобства
        self.ax.grid(True, alpha=0.3)
        
        # Обновляем отображение
        self.canvas.draw()
    
    def save_plot(self):
        # Генерируем имя файла в формате graph{HH}_{MM}_{SS}.png
        now = datetime.datetime.now()
        filename = f"graph{now.hour:02d}_{now.minute:02d}_{now.second:02d}.png"
        
        # Сохраняем текущую фигуру
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"График сохранён как: {filename}")

if __name__ == "__main__":
    # Получаем данные из модуля datatest
    if datatest.df is None:
        print("Ошибка: данные не загружены. Убедитесь, что dataset.csv находится в папке.")
    else:
        root = tk.Tk()
        app = ScatterPlotApp(root, datatest.df)
        root.mainloop()