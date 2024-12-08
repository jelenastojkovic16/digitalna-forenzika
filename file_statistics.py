import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def get_user_input_gui():

    root = tk.Tk()
    root.title("Unos podataka za analizu")


    directory_path = ''
    start_date = None
    end_date = None


    def select_directory():
        directory_path = filedialog.askdirectory()
        entry_directory.delete(0, tk.END)  # Čisti prethodni unos
        entry_directory.insert(0, directory_path)


    def submit_input():
        nonlocal directory_path, start_date, end_date
        directory_path = entry_directory.get()
        start_date_str = entry_start_date.get()
        end_date_str = entry_end_date.get()

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
            root.quit() 
        except Exception as e:
            print(f"Greška prilikom unosa datuma: {e}")
            messagebox.showerror("Greška", "Unesite datum u formatu YYYY-MM-DD!")


    label_directory = tk.Label(root, text="Izaberite direktorijum za analizu:")
    label_directory.pack()

    entry_directory = tk.Entry(root, width=50)
    entry_directory.pack()

    button_browse = tk.Button(root, text="Izaberi direktorijum", command=select_directory)
    button_browse.pack()


    label_start_date = tk.Label(root, text="Unesite početni datum (YYYY-MM-DD):")
    label_start_date.pack()

    entry_start_date = tk.Entry(root)
    entry_start_date.pack()

    label_end_date = tk.Label(root, text="Unesite krajnji datum (YYYY-MM-DD):")
    label_end_date.pack()

    entry_end_date = tk.Entry(root)
    entry_end_date.pack()


    button_submit = tk.Button(root, text="Potvrdi", command=submit_input)
    button_submit.pack()


    root.mainloop()

    return directory_path, start_date, end_date


def collect_data(directory_path, allowed_extensions):
    data = []
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            try:
                file_extension = os.path.splitext(file_name)[1].lstrip('.').lower()
                if file_extension not in allowed_extensions:
                    continue

                stat_info = os.stat(file_path)
                file_size = stat_info.st_size
                last_access_time = datetime.datetime.fromtimestamp(stat_info.st_atime)

                data.append({
                    'path': file_path,
                    'size': file_size,
                    'access_time': last_access_time.isoformat(),
                    'extension': file_extension if file_extension else 'no_extension'
                })
            except Exception as e:
                print(f"Greška prilikom obrade fajla {file_path}: {e}")

    return data

def save_to_csv(data, csv_file_name):
    with open(csv_file_name, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['path', 'size', 'extension', 'access_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Podaci su sačuvani u fajlu: {csv_file_name}")


def analyze_data(file_path, start_date, end_date):
    df = pd.read_csv(file_path)

    df['access_time'] = pd.to_datetime(df['access_time'], format='%Y-%m-%dT%H:%M:%S.%f', errors='coerce')

    df = df[(df['access_time'] >= start_date) & (df['access_time'] <= end_date)]

    df['month'] = df['access_time'].dt.month
    df['day_name'] = df['access_time'].dt.day_name()
    df['hour'] = df['access_time'].dt.hour
    df['date'] = df['access_time'].dt.date
    df['extension'] = df['path'].apply(lambda x: x.split('.')[-1] if '.' in x else 'no_extension')

    monthly_counts = df.groupby('month').size().reindex(range(1, 13), fill_value=0)
    plt.figure(figsize=(10, 6))
    monthly_counts.plot(kind='bar')
    plt.title('Broj pristupa po mesecima')
    plt.xlabel('Mesec')
    plt.ylabel('Broj pristupa')
    plt.xticks(range(12), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=0)
    plt.show()

    extension_counts = df.groupby('extension').size().reset_index(name='count')
    plt.figure(figsize=(10, 6))
    extension_counts.plot(kind='bar', x='extension', y='count', legend=False)
    plt.title('Broj pristupa po ekstenziji fajla')
    plt.xlabel('Ekstenzija fajla')
    plt.ylabel('Broj pristupa')
    plt.xticks(rotation=45)
    plt.show()

    plt.figure(figsize=(10, 6))
    df.groupby('day_name').size().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).plot(kind='bar')
    plt.title('Broj pristupa po danu u nedelji')
    plt.xlabel('Dan u nedelji')
    plt.ylabel('Broj pristupa')
    plt.xticks(rotation=0)
    plt.show()

    hourly_counts = df.groupby('hour').size().reindex(range(24), fill_value=0)
    plt.figure(figsize=(10, 6))
    hourly_counts.plot(kind='bar')
    plt.title('Broj pristupa po satu')
    plt.xlabel('Sat')
    plt.ylabel('Broj pristupa')
    plt.xticks(range(24), range(24), rotation=0)
    plt.show()

    extension_counts_by_date = df.groupby(['date', 'extension']).size().reset_index(name='count')
    fig = px.line(extension_counts_by_date, x='date', y='count', color='extension', title="Broj pristupa po ekstenzijama",
                  labels={'date': 'Datum', 'count': 'Broj pristupa', 'extension': 'Ekstenzija fajla'})
    fig.show()


directory_path, start_date, end_date = get_user_input_gui()

print(f"Direktorijum: {directory_path}")
print(f"Početni datum: {start_date}")
print(f"Krajnji datum: {end_date}")

allowed_extensions = ['pdf', 'txt', 'docx', 'cs', 'js', 'html', 'css', 'rar', 'zip', 'jpg', 'png', 'json']
file_data = collect_data(directory_path, allowed_extensions)
csv_file_name = 'access_log.csv'
save_to_csv(file_data, csv_file_name)

analyze_data(csv_file_name, start_date, end_date)
