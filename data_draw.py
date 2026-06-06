import tkinter as tk
from tkinter import ttk, colorchooser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
import datatest

MARKER_STYLE = 'H'
DEFAULT_CMAP = 'YlOrRd'
DEFAULT_PEN_SIZE = 9
DEFAULT_PEN_COLOR = '#16473d'

COLORMAPS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
    'binary', 'gist_yarg', 'spring', 'summer', 'autumn', 'winter'
]

def shorten_text(text, max_len=20):
    if len(str(text)) > max_len:
        return str(text)[:max_len-3] + '...'
    return str(text)

class DataDrawApp:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.root.title("Data Draw Tool - Задание 4")
        self.root.geometry("1100x700")
        
        self.all_cols = list(df.columns)
        self.numeric_cols = ['order_quantity', 'sales', 'discount', 'discount_value']
        self.numeric_cols = [col for col in self.numeric_cols if col in df.columns]
        
        self.x_var = tk.StringVar(value=self.all_cols[0])
        self.y_var = tk.StringVar(value=self.all_cols[1] if len(self.all_cols) > 1 else self.all_cols[0])
        self.cmap_var = tk.StringVar(value=DEFAULT_CMAP)
        
        self.drawing_mode = False
        self.pen_color = DEFAULT_PEN_COLOR
        self.pen_size = DEFAULT_PEN_SIZE
        self.lines = []  # Список нарисованных линий (объекты Line2D)
        
        self.setup_ui()
        self.update_plot()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_frame, text="Цветовая схема:").pack(side=tk.LEFT, padx=(0, 5))
        cmap_combo = ttk.Combobox(top_frame, textvariable=self.cmap_var, values=COLORMAPS, width=12)
        cmap_combo.pack(side=tk.LEFT)
        cmap_combo.bind('<<ComboboxSelected>>', lambda e: self.update_plot())
        
        ttk.Separator(top_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill='y')
        
        self.draw_btn = ttk.Button(top_frame, text="✏️ Рисование", command=self.toggle_drawing, width=30)
        self.draw_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.color_btn = tk.Button(top_frame, width=3, height=1, bg=self.pen_color, command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(top_frame, text="Толщина:").pack(side=tk.LEFT)
        self.size_spin = ttk.Spinbox(top_frame, from_=1, to=20, width=5, command=self.update_pen_size)
        self.size_spin.set(self.pen_size)
        self.size_spin.pack(side=tk.LEFT)
        
        # Средняя часть
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель (ось X)
        left_frame = ttk.LabelFrame(middle_frame, text="Выбор оси X", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        x_canvas = tk.Canvas(left_frame, width=200, height=400)
        x_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=x_canvas.yview)
        x_scrollable = ttk.Frame(x_canvas)
        
        x_scrollable.bind("<Configure>", lambda e: x_canvas.configure(scrollregion=x_canvas.bbox("all")))
        x_canvas.create_window((0, 0), window=x_scrollable, anchor="nw")
        x_canvas.configure(yscrollcommand=x_scrollbar.set)
        
        for col in self.all_cols:
            btn = ttk.Button(x_scrollable, text=col, width=20,
                            command=lambda c=col: self.set_x_column(c))
            btn.pack(pady=2, fill=tk.X)
        
        x_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        x_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # График
        plot_frame = ttk.Frame(middle_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Нижняя панель (ось Y)
        bottom_frame = ttk.LabelFrame(main_frame, text="Выбор оси Y", padding="5")
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        y_canvas = tk.Canvas(bottom_frame, height=70)
        y_scrollbar = ttk.Scrollbar(bottom_frame, orient="horizontal", command=y_canvas.xview)
        y_scrollable = ttk.Frame(y_canvas)
        
        y_scrollable.bind("<Configure>", lambda e: y_canvas.configure(scrollregion=y_canvas.bbox("all")))
        y_canvas.create_window((0, 0), window=y_scrollable, anchor="nw")
        y_canvas.configure(xscrollcommand=y_scrollbar.set)
        
        for col in self.all_cols:
            btn = ttk.Button(y_scrollable, text=col,
                            command=lambda c=col: self.set_y_column(c))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        y_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        save_btn = ttk.Button(main_frame, text="Сохранить график", command=self.save_plot)
        save_btn.pack(pady=(10, 0))
        
        # События для рисования
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        self.root.bind('<Control-z>', self.undo_last_line)
        self.root.bind('<Control-Z>', self.undo_last_line)
    
    def set_x_column(self, col):
        print(f"Выбрана ось X: {col}")
        self.exit_drawing_mode()
        self.x_var.set(col)
        self.update_plot()
    
    def set_y_column(self, col):
        print(f"Выбрана ось Y: {col}")
        self.exit_drawing_mode()
        self.y_var.set(col)
        self.update_plot()
    
    def toggle_drawing(self):
        if self.drawing_mode:
            self.exit_drawing_mode()
        else:
            self.enter_drawing_mode()
    
    def enter_drawing_mode(self):
        self.drawing_mode = True
        self.draw_btn.config(text="✏️ Рисование (ВКЛ)")
        self.draw_btn.state(['pressed'])
        self.canvas.get_tk_widget().config(cursor="pencil")
        print("Режим рисования ВКЛЮЧЁН")
    
    def exit_drawing_mode(self):
        self.drawing_mode = False
        self.draw_btn.config(text="✏️ Рисование")
        self.draw_btn.state(['!pressed'])
        self.canvas.get_tk_widget().config(cursor="")
        print("Режим рисования ВЫКЛЮЧЕН")
    
    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.pen_color, title="Выберите цвет кисти")
        if color:
            self.pen_color = color[1]
            self.color_btn.config(bg=self.pen_color)
            print(f"Выбран цвет: {self.pen_color}")
    
    def update_pen_size(self):
        self.pen_size = int(self.size_spin.get())
        print(f"Толщина линии: {self.pen_size}")
    
    def on_press(self, event):
        if not self.drawing_mode or event.inaxes != self.ax:
            return
        if event.button == 3:
            self.exit_drawing_mode()
            return
        if event.button == 1:
            self.current_line_start = (event.xdata, event.ydata)
    
    def on_motion(self, event):
        if not self.drawing_mode or not hasattr(self, 'current_line_start') or event.inaxes != self.ax:
            return
        if event.button == 1:
            x1, y1 = self.current_line_start
            x2, y2 = event.xdata, event.ydata
            
            line = plt.Line2D([x1, x2], [y1, y2], linewidth=self.pen_size, color=self.pen_color)
            self.ax.add_line(line)
            self.lines.append(line)
            self.canvas.draw_idle()
            
            self.current_line_start = (x2, y2)
    
    def on_release(self, event):
        if not self.drawing_mode:
            return
        if hasattr(self, 'current_line_start'):
            delattr(self, 'current_line_start')
    
    def undo_last_line(self, event=None):
        if self.lines:
            last_line = self.lines.pop()
            last_line.remove()
            self.canvas.draw_idle()
            print(f"Отменена последняя линия (осталось {len(self.lines)} линий)")
    
    def get_plot_type(self, x_col, y_col):
        x_is_numeric = x_col in self.numeric_cols
        y_is_numeric = y_col in self.numeric_cols
        
        if x_col == y_col:
            return 'histogram' if x_is_numeric else 'pie'
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
        
        print(f"Обновление графика: X={x_col}, Y={y_col}")
        
        # Сохраняем текущие линии
        old_lines = self.lines.copy()
        self.lines = []
        
        # Очищаем оси
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        plot_type = self.get_plot_type(x_col, y_col)
        
        # Получаем данные
        x_data = self.df[x_col].dropna()
        y_data = self.df[y_col].dropna()
        
        # Получаем colormap новым способом
        cmap_obj = plt.colormaps.get(cmap)
        
        if plot_type == 'scatter':
            valid_idx = x_data.index.intersection(y_data.index)
            x_vals = x_data.loc[valid_idx]
            y_vals = y_data.loc[valid_idx]
            self.ax.scatter(x_vals, y_vals, alpha=0.6, s=30, 
                           marker=MARKER_STYLE, c=range(len(x_vals)), cmap=cmap)
            self.ax.set_xlabel(x_col, fontsize=10)
            self.ax.set_ylabel(y_col, fontsize=10)
            self.ax.grid(True, alpha=0.3)
            plt.setp(self.ax.get_xticklabels(), rotation=30, ha='right', fontsize=8)
            
        elif plot_type == 'histogram':
            # histogram - один цвет для всех данных
            self.ax.hist(x_data, bins=10, color=cmap_obj(0.5), edgecolor='black')
            self.ax.set_xlabel(x_col, fontsize=10)
            self.ax.set_ylabel('Частота', fontsize=10)
            self.ax.grid(True, alpha=0.3)
            plt.setp(self.ax.get_xticklabels(), rotation=30, ha='right', fontsize=8)
            
        elif plot_type == 'pie':
            counts = x_data.value_counts()
            if len(counts) > 0:
                labels = [shorten_text(str(label), 18) for label in counts.index]
                colors_list = [cmap_obj(i / len(counts)) for i in range(len(counts))]
                self.ax.pie(counts.values, labels=labels, autopct='%1.1f%%', colors=colors_list)
                self.ax.set_title(f'Круговая диаграмма: {x_col}', fontsize=12)
            
        elif plot_type == 'bar':
            counts = x_data.value_counts()
            if len(counts) > 0:
                labels = [shorten_text(str(label), 15) for label in counts.index]
                colors_list = [cmap_obj(i / len(counts)) for i in range(len(counts))]
                self.ax.bar(range(len(counts)), counts.values, color=colors_list)
                self.ax.set_xticks(range(len(counts)))
                self.ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            self.ax.set_xlabel(x_col, fontsize=10)
            self.ax.set_ylabel('Количество', fontsize=10)
            self.ax.set_title(f'Столбчатая диаграмма: {x_col}', fontsize=12)
            self.ax.grid(True, alpha=0.3, axis='y')
            
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
                bp = self.ax.boxplot(data_to_plot, tick_labels=short_categories, patch_artist=True)
                for patch, idx in zip(bp['boxes'], range(len(categories))):
                    patch.set_facecolor(cmap_obj(idx / len(categories)))
            self.ax.set_xlabel(y_col, fontsize=10)
            self.ax.set_ylabel(x_col, fontsize=10)
            self.ax.set_title(f'Ящик с усами: {x_col} по категориям {y_col}', fontsize=12)
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
            self.ax.grid(True, alpha=0.3, axis='y')
        
        self.ax.set_title(f'{plot_type.capitalize()}: {x_col} vs {y_col}', fontsize=12)
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()
        
        # Восстанавливаем нарисованные линии
        for line in old_lines:
            self.ax.add_line(line)
            self.lines.append(line)
        self.canvas.draw_idle()
        
        print("График обновлён")
    
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
        app = DataDrawApp(root, datatest.df)
        root.mainloop()