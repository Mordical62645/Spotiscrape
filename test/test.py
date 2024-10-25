import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re

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
        if not date:
            date = "Date not found"
        
        tables = soup.find_all('table')
        if not tables:
            print("No tables found on the page.")
            return pd.DataFrame()

        table = tables[0]
        rows = table.find_all('tr')
        if len(rows) < 2:
            print("No chart data found in the table.")
            return pd.DataFrame()

        songs_data = []
        for row in rows[1:]:
            columns = row.find_all('td')
            if len(columns) >= 11: 
                try:
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

        print(f"Spotify Daily Chart - Philippines - {date}")
        return pd.DataFrame(songs_data)
    else:
        print("Failed to retrieve the Kworb chart.")
        return pd.DataFrame()

# Display all relevant data and simultaneous visualizations
def display_all(data):
    # Full Chart Data
    print("Full Chart Data:")
    print(data)

    # Top 10 Songs
    top_10 = data.head(10).copy() 
    print("\nTop 10 Songs:")
    print(top_10)

    # Prediction for Next Week
    top_10['Predicted Streams (Next Week)'] = top_10['Streams'] * 1.10
    print("\nPredicted Streams for Top 10 Songs (Next Week):")
    print(top_10[['Artist and Title', 'Predicted Streams (Next Week)']])

    # Prediction for Next Month
    top_10['Predicted Streams (Next Month)'] = top_10['Streams'] * (1.10 ** 4)
    print("\nPredicted Streams for Top 10 Songs (Next Month):")
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
    data = scrape_kworb_philippines()
    
    if not data.empty:
        display_all(data)  # Display all data and simultaneous visualizations
