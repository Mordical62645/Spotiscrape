import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re
import os
from datetime import datetime
import zipfile
import openpyxl
import tkinter as tk
from tkinter import messagebox
from sklearn.linear_model import LinearRegression
import numpy as np


# Font
plt.rcParams['font.family'] = 'Arial'  # Change as necessary

# Clean text by removing non-ASCII characters
def clean_text(text):
    return text.strip() and re.sub(r'[^\x20-\x7E]+', '', text)

def scrape_kworb_philippines():
    url = "https://kworb.net/spotify/country/ph_daily.html"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the date from the header or other relevant text
        date = None
        for element in soup.find_all(string=re.compile(r'\d{4}/\d{2}/\d{2}')):
            date_match = re.search(r'\d{4}/\d{2}/\d{2}', element)
            if date_match:
                date = date_match.group(0)
                break

        if date is None:
            date = "Date not found"

        print(f"Extracted Date: {date}")
        
        tables = soup.find_all('table')
        if not tables:
            print("No tables found on the page.")
            return pd.DataFrame(), date  # Return empty DataFrame and date

        table = tables[0]
        rows = table.find_all('tr')
        if len(rows) < 2:
            print("No chart data found in the table.")
            return pd.DataFrame(), date  # Return empty DataFrame and date

        songs_data = []
        for row in rows[1:]:
            columns = row.find_all('td')
            if len(columns) >= 11: 
                try:
                    # Extract song data
                    pos = columns[0].text.strip() 
                    p_plus = columns[1].text.strip()  
                    artist_and_title = clean_text(columns[2].text.strip()) 
                    days = columns[3].text.strip()  
                    pk = columns[4].text.strip()  
                    x = columns[5].text.strip()  
                    streams = columns[6].text.strip().replace(',', '')  
                    streams_plus = columns[7].text.strip().replace(',', '') 
                    seven_day = columns[8].text.strip().replace(',', '')  
                    seven_day_plus = columns[9].text.strip().replace(',', '')  
                    total = columns[10].text.strip().replace(',', '')  

                    # Convert streams and other numerical data to integers
                    streams = int(streams) if streams.isdigit() else 0
                    streams_plus = int(streams_plus) if streams_plus.replace('-', '').isdigit() else 0
                    seven_day = int(seven_day) if seven_day.isdigit() else 0
                    seven_day_plus = int(seven_day_plus) if seven_day_plus.replace('-', '').isdigit() else 0
                    total = int(total) if total.isdigit() else 0

                    songs_data.append({
                        "Pos": pos,
                        "P+": p_plus,
                        "Artist and Title": artist_and_title,
                        "Days": days,
                        "Pk": pk,
                        "(x?)": x,
                        "Streams": streams,
                        "Streams+": streams_plus,
                        "7Day": seven_day,
                        "7Day+": seven_day_plus,
                        "Total": total
                    })

                except (ValueError, IndexError) as e:
                    print(f"Error processing row: {e}")
                    continue

        print(f"Spotify Daily Chart - Philippines - {date}")  # Display date
        return pd.DataFrame(songs_data), date  # Return DataFrame and date
    else:
        print("Failed to retrieve the Kworb chart.")
        return pd.DataFrame(), "Date not found"  # Return empty DataFrame and date

# New function to get the scraped date
def get_scraped_date():
    data, date = scrape_kworb_philippines()
    return date

def linear_regression_predictions(data, song_index):
    # Prepare the data for the specific song
    X = np.arange(len(data)).reshape(-1, 1)  # X is the index of all songs
    y = data['Streams'].values  # y is the stream values

    model = LinearRegression()
    model.fit(X, y)

    # Predict for the specific song index for next week and next month
    next_week_index = song_index + 1  # Predicting for the next week
    next_month_index = song_index + 4  # Predicting for the next month
    
    # Using the model to predict the streams
    next_week_prediction = model.predict([[next_week_index]])[0]
    next_month_prediction = model.predict([[next_month_index]])[0]
    
    return next_week_prediction, next_month_prediction

# Function to get the Downloads directory path
def get_downloads_path():
    home = os.path.expanduser("~")
    return os.path.join(home, 'Downloads')

# Function to generate the filename with date and time
def generate_filename(prefix):
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{prefix}SpotiScrape-{current_time}.csv", current_time  # Return the current time for zip filename

def convert_to_xlsx(data):
    downloads_path = get_downloads_path()

    # Filter the top 10 data for the current week
    top_10 = data.head(10).copy()

    # Generate filenames and save current week data to XLSX
    cw_filename, current_time = generate_filename("[CW]")
    cw_xlsx_path = os.path.join(downloads_path, cw_filename.replace(".csv", ".xlsx"))
    top_10.to_excel(cw_xlsx_path, index=False)  # Save top_10, not data

    # Predictions for next week and next month for each song in top_10
    predictions_next_week = []
    predictions_next_month = []

    for i in range(len(top_10)):
        next_week_prediction, next_month_prediction = linear_regression_predictions(data, i)
        predictions_next_week.append(next_week_prediction)
        predictions_next_month.append(next_month_prediction)

    # Add predictions to the top_10 DataFrame
    top_10['Predicted Streams (Next Week)'] = predictions_next_week
    top_10['Predicted Streams (Next Month)'] = predictions_next_month

    # Save predictions to XLSX
    nw_filename, _ = generate_filename("[NW]")
    nw_xlsx_path = os.path.join(downloads_path, nw_filename.replace(".csv", ".xlsx"))
    top_10[['Artist and Title', 'Predicted Streams (Next Week)']].to_excel(nw_xlsx_path, index=False)
    
    nm_filename, _ = generate_filename("[NM]")
    nm_xlsx_path = os.path.join(downloads_path, nm_filename.replace(".csv", ".xlsx"))
    top_10[['Artist and Title', 'Predicted Streams (Next Month)']].to_excel(nm_xlsx_path, index=False)

    # Create a ZIP file
    zip_filename = f"SpotiScrape-{current_time}.zip"
    with zipfile.ZipFile(os.path.join(downloads_path, zip_filename), 'w') as zipf:
        for xlsx_path in [cw_xlsx_path, nw_xlsx_path, nm_xlsx_path]:
            zipf.write(xlsx_path, arcname=os.path.basename(xlsx_path))
            os.remove(xlsx_path)

    print(f"Saved all files in {zip_filename} in Downloads.")
    messagebox.showinfo("Success", f"{zip_filename} is successfully saved in Downloads")

def convert_to_csv(data):
    downloads_path = get_downloads_path()

    # Filter the top 10 data for the current week
    top_10 = data.head(10).copy()

    # Generate filenames and save current week data to CSV
    cw_filename, current_time = generate_filename("[CW]")
    cw_csv_path = os.path.join(downloads_path, cw_filename)
    top_10.to_csv(cw_csv_path, index=False)

    # Predictions for next week and next month for each song in top_10
    predictions_next_week = []
    predictions_next_month = []

    for i in range(len(top_10)):
        next_week_prediction, next_month_prediction = linear_regression_predictions(data, i)
        predictions_next_week.append(next_week_prediction)
        predictions_next_month.append(next_month_prediction)

    # Add predictions to the top_10 DataFrame
    top_10['Predicted Streams (Next Week)'] = predictions_next_week
    top_10['Predicted Streams (Next Month)'] = predictions_next_month

    # Save predictions to CSV
    nw_filename, _ = generate_filename("[NW]")
    nw_csv_path = os.path.join(downloads_path, nw_filename)
    top_10[['Artist and Title', 'Predicted Streams (Next Week)']].to_csv(nw_csv_path, index=False)

    nm_filename, _ = generate_filename("[NM]")
    nm_csv_path = os.path.join(downloads_path, nm_filename)
    top_10[['Artist and Title', 'Predicted Streams (Next Month)']].to_csv(nm_csv_path, index=False)

    # Create a ZIP file
    zip_filename = f"SpotiScrape-{current_time}.zip"
    with zipfile.ZipFile(os.path.join(downloads_path, zip_filename), 'w') as zipf:
        for filename in [cw_filename, nw_filename, nm_filename]:
            file_path = os.path.join(downloads_path, filename)
            zipf.write(file_path, arcname=filename)
            os.remove(file_path)

    print(f"Saved all files in {zip_filename} in Downloads.")
    messagebox.showinfo("Success", f"{zip_filename} is successfully saved in Downloads")
    
def display_all(data):
    # Top 10 Songs
    top_10 = data.head(10).copy()
    print("\nTop 10 Songs (Current Week):")
    print(top_10)

    # Get predictions for next week and next month for each song in top_10
    top_10['Predicted Streams (Next Week)'] = top_10.index.map(lambda x: linear_regression_predictions(data, x)[0])
    top_10['Predicted Streams (Next Month)'] = top_10.index.map(lambda x: linear_regression_predictions(data, x)[1])

    print("\nTop 10 Songs (Next Week):")
    print(top_10[['Artist and Title', 'Predicted Streams (Next Week)']])

    print("\nTop 10 Songs (Next Month):")
    print(top_10[['Artist and Title', 'Predicted Streams (Next Month)']])

    # Line Chart for Streams (Current, Next Week, Next Month)
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # Jitter offset for x-axis to avoid overlapping
    jitter = np.linspace(-0.1, 0.1, len(top_10))  # Small unique offset for each song

    for i, (_, row) in enumerate(top_10.iterrows()):
        x = [0 + jitter[i], 1 + jitter[i], 2 + jitter[i]]  # Slightly offset x-axis positions
        y = [row['Streams'], row['Predicted Streams (Next Week)'], row['Predicted Streams (Next Month)']]
        ax.plot(x, y, marker='o', label=row['Artist and Title'])
    
    ax.set_xticks([0, 1, 2])  # Explicit x-tick positions
    ax.set_xticklabels(['Current Week', 'Next Week', 'Next Month'])
    ax.set_xlabel('Time')
    ax.set_ylabel('Streams')
    ax.set_title('Current and Predicted Streams for Top 10 Songs')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    ax.grid(True)

    # Adjust y-axis limits if values are very close
    all_streams = top_10[['Streams', 'Predicted Streams (Next Week)', 'Predicted Streams (Next Month)']].values.flatten()
    ax.set_ylim([min(all_streams) * 0.9, max(all_streams) * 1.1])

    plt.tight_layout()

    # plt.show()
    return top_10['Predicted Streams (Next Week)'], top_10['Predicted Streams (Next Month)'] ,fig

if __name__ == "__main__":
    data, date = scrape_kworb_philippines()  # Now fetching date as well
    
    if not data.empty:
        display_all(data)  # Display all data and simultaneous visualizations
        convert_to_xlsx(data) # test
        convert_to_csv(data) # test

