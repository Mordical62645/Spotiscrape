# gui_test.py
import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import sys
import os
import shutil
from main import scrape_kworb_philippines  # Ensure this function is correctly defined
from main import get_scraped_date  # Import the function that gets the scraped date
from main import display_all

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self, data):
        super().__init__()

        self.is_refreshing = False
        self.after_ids = []  # Store after IDs for cancellation

        # Configure window
        self.title("SpotiScrape - Spotify Top Charts Philippines")
        self.geometry("1100x580")
        self.resizable(False, False)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Scrollable frame
        self.grid_rowconfigure(0, weight=1)      # For tab view

        # Create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="SpotiScrape", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Get the scraped date from logic.py
        scraped_date = get_scraped_date()  # Assuming this returns the date as a string

        # Create a label to display the date
        self.date_label = customtkinter.CTkLabel(self.sidebar_frame, text=f"Date: {scraped_date}", font=customtkinter.CTkFont(size=12))
        self.date_label.grid(row=1, column=0, padx=20, pady=(0, 10))

        # Create sidebar buttons
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.convert_to_csv, text="Convert to CSV")
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.convert_to_xlsx, text="Convert to XLSX")
        self.sidebar_button_2.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.refresh_data, text="Refresh Data")
        self.sidebar_button_3.grid(row=4, column=0, padx=20, pady=10)

        # Appearance settings
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                        command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                                command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # Create scrollable frame for the tabview
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, width=250)
        self.scrollable_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Create tabview inside the scrollable frame
        self.tabview = customtkinter.CTkTabview(self.scrollable_frame, width=250)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tabview.add("Current Week")
        self.tabview.add("Prediction: Next Week")
        self.tabview.add("Prediction: Next Month")

        # Create content for each tab
        self.create_tab_content(self.tabview.tab("Current Week"), data.head(10), "Current Week Data", 'current')
        self.create_tab_content(self.tabview.tab("Prediction: Next Week"), data.head(10).copy(), "Next Week Prediction", 'next')
        self.create_tab_content(self.tabview.tab("Prediction: Next Month"), data.head(10).copy(), "Next Month Prediction", 'month')

        # Set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

        # Bind the close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_tab_content(self, tab, data, initial_text, prediction_type):
        # Create a frame to hold the canvas and textbox
        content_frame = customtkinter.CTkFrame(tab)
        content_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")

        # Create a canvas for the chart
        self.chart_frame = customtkinter.CTkFrame(content_frame)
        self.chart_frame.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="nsew")

        # Create a Matplotlib figure based on the data
        fig, ax = plt.subplots()
        if prediction_type == 'current':
            ax.barh(data['Artist and Title'], data['Streams'], color='skyblue')
            ax.set_title('Top 10 Songs in the Philippines (Current Week)')
            predicted_streams_column = False  # No predicted streams in current
        else:
            # Create the predicted streams column for next week and month
            if prediction_type == 'next':
                data.loc[:, 'Predicted Streams'] = data['Streams'] * 1.10
            elif prediction_type == 'month':
                data.loc[:, 'Predicted Streams'] = data['Streams'] * (1.10 ** 4)

            ax.barh(data['Artist and Title'], data['Predicted Streams'], color='lightgreen' if prediction_type == 'next' else 'salmon')
            ax.set_title(f'Predicted Streams for Top 10 Songs ({prediction_type})')
            predicted_streams_column = True  # Predicted streams is now available

        # Create a FigureCanvasTkAgg to embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Create a text box within the frame
        self.textbox = customtkinter.CTkTextbox(content_frame, state="normal", font=("Courier New", 10))
        self.textbox.grid(row=1, column=0, padx=(0, 5), pady=(0, 0), sticky="nsew")

        # Set character limit
        char_limit = 30

        # Format the data for the textbox
        formatted_text = initial_text + "\n\n"
        formatted_text += f"{'Pos':<5} {'P+':<5} {'Artist and Title':<{char_limit}} {'Pk':<5} {'Streams':<10} {'7Day':<10} {'Total':<10} {'Predicted':<10}\n"
        formatted_text += "-" * 80 + "\n"

        for index, row in data.iterrows():
            artist_title = row['Artist and Title']
            # Truncate artist and title if it exceeds the character limit
            if len(artist_title) > char_limit:
                artist_title = artist_title[:char_limit - 3] + "..."  # Keep space for ellipsis
            
            if predicted_streams_column:
                formatted_text += f"{row['Pos']:<5} {row['P+']:<5} {artist_title:<{char_limit}} {row['Pk']:<5} {row['Streams']:<10} {row['7Day']:<10} {row['Total']:<10} {row['Predicted Streams']:<10}\n"
            else:
                formatted_text += f"{row['Pos']:<5} {row['P+']:<5} {artist_title:<{char_limit}} {row['Pk']:<5} {row['Streams']:<10} {row['7Day']:<10} {row['Total']:<10}\n"

        self.textbox.insert("0.0", formatted_text)
        self.textbox.configure(state="disabled")

    def refresh_data(self):
        print("Refresh Data Clicked")
        # Clear existing after IDs
        for after_id in self.after_ids:
            self.after_cancel(after_id)
        self.after_ids.clear()

        if self.is_refreshing:
            return  # Already refreshing

        self.is_refreshing = True
        self.sidebar_button_3.configure(state="disabled")  # Disable the button while refreshing

        # Simulate data refresh
        self.after_ids.append(self.after(2000, self.update_data))  # Schedule the update after 2 seconds

    def update_data(self):
        # Logic to update data here
        new_data, date = scrape_kworb_philippines()  # Unpack the tuple here
        self.date_label.configure(text=f"Date: {date}")  # Update the date label
        self.create_tab_content(self.tabview.tab("Current Week"), new_data.head(10), "Current Week Data", 'current')
        self.create_tab_content(self.tabview.tab("Prediction: Next Week"), new_data.head(10).copy(), "Next Week Prediction", 'next')
        self.create_tab_content(self.tabview.tab("Prediction: Next Month"), new_data.head(10).copy(), "Next Month Prediction", 'month')
        
        self.is_refreshing = False
        self.sidebar_button_3.configure(state="normal")  # Re-enable the button

    def convert_to_csv(self):
        print("Convert to CSV Clicked")

    def convert_to_xlsx(self):
        print("Convert to XLSX Clicked")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling):
        customtkinter.set_widget_scaling(float(new_scaling[:-1]) / 100)

    def on_closing(self):
        # Remove the __pycache__ directory if it exists
        pycache_path = "__pycache__"
        if os.path.exists(pycache_path):
            try:
                shutil.rmtree(pycache_path)
                print(f"Removed {pycache_path} directory.")
            except Exception as e:
                print(f"Error removing {pycache_path}: {e}")  # Log the error

        sys.exit()  # Exit the program

if __name__ == "__main__":
    data, date = scrape_kworb_philippines()  # Unpack the tuple here
    
    if not data.empty:
        print(f"Extracted Date: {date}")  # Optional: display the date if needed
        app = App(data)  # Pass the DataFrame to the App
        app.mainloop()
    else:
        print("No data to display.")