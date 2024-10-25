import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re
import os
from datetime import datetime
import zipfile
import openpyxl

# Font
plt.rcParams['font.family'] = 'Liberation Sans'  # Change as necessary

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

# Function to get the Downloads directory path
def get_downloads_path():
    home = os.path.expanduser("~")
    return os.path.join(home, 'Downloads')

# Function to generate the filename with date and time
def generate_filename(prefix):
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{prefix}SpotiScrape-{current_time}.csv", current_time  # Return the current time for zip filename

# Function to convert top 10 data to CSV, create ZIP, and save in Downloads
def convert_to_csv(data):
    downloads_path = get_downloads_path()
    # Filter the top 10 data for the current week
    top_10 = data.head(10).copy()
    # Generate filenames and save current week data
    cw_filename, current_time = generate_filename("[CW]")
    data.to_csv(os.path.join(downloads_path, cw_filename), index=False)

    # Predictions for next week and next month
    top_10['Predicted Streams (Next Week)'] = top_10['Streams'] * 1.10
    top_10['Predicted Streams (Next Month)'] = top_10['Streams'] * (1.10 ** 4)

    # Save next week and next month data
    nw_filename, _ = generate_filename("[NW]")
    top_10[['Artist and Title', 'Predicted Streams (Next Week)']].to_csv(os.path.join(downloads_path, nw_filename), index=False)
    
    nm_filename, _ = generate_filename("[NM]")
    top_10[['Artist and Title', 'Predicted Streams (Next Month)']].to_csv(os.path.join(downloads_path, nm_filename), index=False)

    # Create a ZIP file
    zip_filename = f"SpotiScrape-{current_time}.zip"
    with zipfile.ZipFile(os.path.join(downloads_path, zip_filename), 'w') as zipf:
        # Write each CSV to the ZIP and then delete
        for filename in [cw_filename, nw_filename, nm_filename]:
            file_path = os.path.join(downloads_path, filename)
            zipf.write(file_path, arcname=filename)
            os.remove(file_path)  # Delete the individual CSV after adding it to the ZIP

    print(f"Saved all files in {zip_filename} in Downloads.")

# Function to convert top 10 data to XLSX, create ZIP, and save in Downloads
def convert_to_xlsx(data):
    downloads_path = get_downloads_path()
    # Filter the top 10 data for the current week
    top_10 = data.head(10).copy()

    # Generate filenames and save current week data to XLSX
    cw_filename, current_time = generate_filename("[CW]")
    cw_xlsx_path = os.path.join(downloads_path, cw_filename.replace(".csv", ".xlsx"))
    data.to_excel(cw_xlsx_path, index=False)

    # Predictions for next week and next month
    top_10['Predicted Streams (Next Week)'] = top_10['Streams'] * 1.10
    top_10['Predicted Streams (Next Month)'] = top_10['Streams'] * (1.10 ** 4)

    # Save next week and next month data to XLSX
    nw_filename, _ = generate_filename("[NW]")
    nw_xlsx_path = os.path.join(downloads_path, nw_filename.replace(".csv", ".xlsx"))
    top_10[['Artist and Title', 'Predicted Streams (Next Week)']].to_excel(nw_xlsx_path, index=False)
    
    nm_filename, _ = generate_filename("[NM]")
    nm_xlsx_path = os.path.join(downloads_path, nm_filename.replace(".csv", ".xlsx"))
    top_10[['Artist and Title', 'Predicted Streams (Next Month)']].to_excel(nm_xlsx_path, index=False)

    # Create a ZIP file
    zip_filename = f"SpotiScrape-{current_time}.zip"
    with zipfile.ZipFile(os.path.join(downloads_path, zip_filename), 'w') as zipf:
        # Write each XLSX to the ZIP and then delete
        for xlsx_path in [cw_xlsx_path, nw_xlsx_path, nm_xlsx_path]:
            zipf.write(xlsx_path, arcname=os.path.basename(xlsx_path))
            os.remove(xlsx_path)  # Delete the individual XLSX after adding it to the ZIP

    print(f"Saved all files in {zip_filename} in Downloads.")

# Display all relevant data and simultaneous visualizations
def display_all(data):
    # Full Chart Data
    print("Full Chart Data:")
    print(data)

    # Top 10 Songs
    top_10 = data.head(10).copy() 
    print("\nTop 10 Songs (Current Week):")
    print(top_10)

    # Prediction for Next Week
    top_10['Predicted Streams (Next Week)'] = top_10['Streams'] * 1.10
    
    # Prediction for Next Month
    top_10['Predicted Streams (Next Month)'] = top_10['Streams'] * (1.10 ** 4)
    
    # Print predictions for Next Week and Next Month
    print("\nTop 10 Songs (Predicted Streams for Next Week):")
    print(top_10[['Artist and Title', 'Predicted Streams (Next Week)']])

    print("\nTop 10 Songs (Predicted Streams for Next Month):")
    print(top_10[['Artist and Title', 'Predicted Streams (Next Month)']])

    # Visualization for Top 10 Current Week Streams
    plt.figure()
    plt.barh(top_10['Artist and Title'], top_10['Streams'], color='skyblue')
    plt.xlabel('Streams')
    plt.title('Top 10 Songs in the Philippines (Current Week)')
    plt.gca().invert_yaxis()

    # Visualization for Predicted Streams Next Week
    plt.figure()
    plt.barh(top_10['Artist and Title'], top_10['Predicted Streams (Next Week)'], color='lightgreen')
    plt.xlabel('Predicted Streams (Next Week)')
    plt.title('Predicted Streams for Top 10 Songs (Next Week)')
    plt.gca().invert_yaxis()

    # Visualization for Predicted Streams Next Month
    plt.figure()
    plt.barh(top_10['Artist and Title'], top_10['Predicted Streams (Next Month)'], color='salmon')
    plt.xlabel('Predicted Streams (Next Month)')
    plt.title('Predicted Streams for Top 10 Songs (Next Month)')
    plt.gca().invert_yaxis()

    plt.show()  # Show all charts at once

if __name__ == "__main__":
    data, date = scrape_kworb_philippines()  # Now fetching date as well
    
    if not data.empty:
        convert_to_xlsx(data) # test
        display_all(data)  # Display all data and simultaneous visualizations
