import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
import datatest

# Индивидуальные настройки
MARKER_STYLE = 'H'           # Шестиугольник
DEFAULT_CMAP = 'YlOrRd'      # Буква 'М' -> цветовая схема YlOrRd

# Список из 29 цветовых схем
COLORMAPS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
    'binary', 'gist_yarg', 'spring', 'summer', 'autumn', 'winter'
]

def shorten_text(text, max_len=22):
    if len(str(text)) > max_len:
        return str(text)[:max_len-3] + '...'
    return str(text)

class DataVisualApp:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.root.title("Data Visual Tool - Задание 3")
        self.root.geometry("1100x700")
        
        # Все колонки для выбора
        self.all_cols = list(df.columns)
        self.numeric_cols = ['order_quantity', 'sales', 'discount', 'discount_value']
        self.numeric_cols = [col for col in self.numeric_cols if col in df.columns]
        
        # Сокращённые названия для отображения на кнопках
        self.col_display_names = {col: shorten_text(col, 22) for col in self.all_cols}
        
        self.x_var = tk.StringVar(value=self.all_cols[0])
        self.y_var = tk.StringVar(value=self.all_cols[1] if len(self.all_cols) > 1 else self.all_cols[0])
        self.cmap_var = tk.StringVar(value=DEFAULT_CMAP)
        
        self.setup_ui()
        self.update_plot()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Верхняя панель
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(top_frame, text="Цветовая схема:").pack(side=tk.LEFT, padx=(0, 5))
        cmap_combo = ttk.Combobox(top_frame, textvariable=self.cmap_var, values=COLORMAPS, width=15)
        cmap_combo.pack(side=tk.LEFT)
        cmap_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        # Левая панель - ось X
        left_frame = ttk.LabelFrame(main_frame, text="Выбор оси X", padding="5")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        left_canvas = tk.Canvas(left_frame, height=400)
        left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
        left_scrollable = ttk.Frame(left_canvas)
        
        left_scrollable.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left_scrollable, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        for col in self.all_cols:
            btn = ttk.Button(left_scrollable, text=self.col_display_names[col], width=22,
                            command=lambda c=col: self.set_x_column(c))
            btn.pack(pady=2, fill='x')
        
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")
        
        # Центральная панель - график
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Нижняя панель - ось Y
        bottom_frame = ttk.LabelFrame(main_frame, text="Выбор оси Y", padding="5")
        bottom_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        bottom_canvas = tk.Canvas(bottom_frame, height=70)
        bottom_scrollbar = ttk.Scrollbar(bottom_frame, orient="horizontal", command=bottom_canvas.xview)
        bottom_scrollable = ttk.Frame(bottom_canvas)
        
        bottom_scrollable.bind("<Configure>", lambda e: bottom_canvas.configure(scrollregion=bottom_canvas.bbox("all")))
        bottom_canvas.create_window((0, 0), window=bottom_scrollable, anchor="nw")
        bottom_canvas.configure(xscrollcommand=bottom_scrollbar.set)
        
        for col in self.all_cols:
            btn = ttk.Button(bottom_scrollable, text=self.col_display_names[col],
                            command=lambda c=col: self.set_y_column(c))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        bottom_canvas.pack(side="top", fill="both", expand=True)
        bottom_scrollbar.pack(side="bottom", fill="x")
        
        # Кнопка сохранения
        save_btn = ttk.Button(main_frame, text="Сохранить график", command=self.save_plot)
        save_btn.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # Настройка весов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(1, weight=1)
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
    
    def set_x_column(self, col):
        self.x_var.set(col)
        self.update_plot()
    
    def set_y_column(self, col):
        self.y_var.set(col)
        self.update_plot()
    
    def get_plot_type(self, x_col, y_col):
        x_is_numeric = x_col in self.numeric_cols
        y_is_numeric = y_col in self.numeric_cols
        
        if x_col == y_col:
            if x_is_numeric:
                return 'histogram'
            else:
                return 'pie'
        elif x_is_numeric and not y_is_numeric:
            return 'boxplot'
        elif not x_is_numeric and y_is_numeric:
            return 'bar'
        else:
            return 'scatter'
    
    def update_plot(self):
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        cmap = self.cmap_var.get()
        
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        plot_type = self.get_plot_type(x_col, y_col)
        
        # Исправлено: берём одну колонку как Series
        x_data = self.df[x_col].dropna()
        y_data = self.df[y_col].dropna()
        
        # Получаем colormap новым способом (без DeprecationWarning)
        cmap_obj = plt.colormaps.get(cmap)
        
        if plot_type == 'scatter':
            # Для scatter нужны общие индексы
            valid_idx = x_data.index.intersection(y_data.index)
            x_vals = x_data.loc[valid_idx]
            y_vals = y_data.loc[valid_idx]
            colors = cmap_obj(range(len(x_vals)))
            ax.scatter(x_vals, y_vals, alpha=0.6, s=30, 
                       marker=MARKER_STYLE, c=range(len(x_vals)), cmap=cmap)
            ax.set_xlabel(x_col, fontsize=10)
            ax.set_ylabel(y_col, fontsize=10)
            ax.set_title(f'Scatter Plot: {x_col} vs {y_col}', fontsize=12)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=8)
            
        elif plot_type == 'histogram':
            ax.hist(x_data, bins=10, color=cmap_obj(0.5), edgecolor='black')
            ax.set_xlabel(x_col, fontsize=10)
            ax.set_ylabel('Частота', fontsize=10)
            ax.set_title(f'Гистограмма: {x_col}', fontsize=12)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=8)
            
        elif plot_type == 'pie':
            counts = x_data.value_counts()
            if len(counts) > 0:
                labels = [shorten_text(str(label), 18) for label in counts.index]
                colors_list = [cmap_obj(i / len(counts)) for i in range(len(counts))]
                ax.pie(counts.values, labels=labels, autopct='%1.1f%%', colors=colors_list)
                ax.set_title(f'Круговая диаграмма: {x_col}', fontsize=12)
            
        elif plot_type == 'bar':
            counts = x_data.value_counts()
            if len(counts) > 0:
                labels = [shorten_text(str(label), 15) for label in counts.index]
                colors_list = [cmap_obj(i / len(counts)) for i in range(len(counts))]
                ax.bar(range(len(counts)), counts.values, color=colors_list)
                ax.set_xticks(range(len(counts)))
                ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            ax.set_xlabel(x_col, fontsize=10)
            ax.set_ylabel('Количество', fontsize=10)
            ax.set_title(f'Столбчатая диаграмма: {x_col}', fontsize=12)
            ax.grid(True, alpha=0.3, axis='y')
            
        elif plot_type == 'boxplot':
            categories = y_data.unique()
            if len(categories) > 0:
                short_categories = [shorten_text(str(cat), 12) for cat in categories]
                data_to_plot = []
                for cat in categories:
                    cat_data = self.df[self.df[y_col] == cat][x_col].dropna().values
                    if len(cat_data) > 0:
                        data_to_plot.append(cat_data)
                    else:
                        data_to_plot.append([0])
                bp = ax.boxplot(data_to_plot, tick_labels=short_categories, patch_artist=True)
                for patch, idx in zip(bp['boxes'], range(len(categories))):
                    patch.set_facecolor(cmap_obj(idx / len(categories)))
            ax.set_xlabel(y_col, fontsize=10)
            ax.set_ylabel(x_col, fontsize=10)
            ax.set_title(f'Ящик с усами: {x_col} по категориям {y_col}', fontsize=12)
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
            ax.grid(True, alpha=0.3, axis='y')
        
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()
    
    def save_plot(self):
        now = datetime.datetime.now()
        filename = f"graph{now.hour:02d}_{now.minute:02d}_{now.second:02d}.png"
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"График сохранён как: {filename}")

if __name__ == "__main__":
    if datatest.df is None:
        print("Ошибка: данные не загружены.")
    else:
        root = tk.Tk()
        app = DataVisualApp(root, datatest.df)
        root.mainloop()