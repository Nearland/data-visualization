import pandas as pd
import sys

# Глобальная переменная для хранения данных
df = None

def load_dataset(file_path='dataset.csv'):
    """Загружает CSV и возвращает DataFrame."""
    try:
        return pd.read_csv(file_path, index_col=0)
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        sys.exit(1)

# Определяем, какие колонки считать счётными (числовыми), а какие категориальными
NUMERIC_COLS = ['order_quantity', 'sales', 'discount', 'discount_value']
CATEGORICAL_COLS = ['order_status', 'customer', 'product_category', 'product_sub_category']

def print_report(df):
    # Выводит отчёт в консоль и в файл report.txt
    original_stdout = sys.stdout
    try:
        with open('report.txt', 'w', encoding='utf-8') as f:
            sys.stdout = f
            
            print(f"Размерность датасета: {df.shape}")
            print("-" * 40)
            
            from io import StringIO
            buffer = StringIO()
            df.info(buf=buffer)
            info_str = buffer.getvalue()
            print(info_str)
            print("-" * 40)
            
            print("Количество пропусков (NaN) по колонкам:")
            print(df.isnull().sum())
            print("-" * 40)
            
            print("Базовая статистика для числовых (счётных) колонок:")
            print("Колонка\t\tсреднее\t\tмедиана\t\tотклонение")
            for col in NUMERIC_COLS:
                if col in df.columns:
                    mean_val = df[col].mean()
                    median_val = df[col].median()
                    std_val = df[col].std()
                    print(f"{col}\t\t{mean_val:.2f}\t\t{median_val:.2f}\t\t{std_val:.2f}")
            print("-" * 40)
            
            print("Статистика для категориальных колонок:")
            for col in CATEGORICAL_COLS:
                if col in df.columns:
                    print(f"\n{col}:")
                    print(df[col].value_counts())
                    print("-" * 20)
            
    finally:
        sys.stdout = original_stdout
    
    print("Отчёт сохранён в 'report.txt'. Содержимое отчёта:\n")
    with open('report.txt', 'r', encoding='utf-8') as f:
        print(f.read())

if __name__ == "__main__":
    df = load_dataset()
    # Выводим отчёт
    print_report(df)
else:
    df = load_dataset()