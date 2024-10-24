import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("SpotiScrape - Spotify Top Charts Philippines")
        self.geometry(f"{1100}x{580}")
        self.resizable(False, False) 

        # Prevent fullscreen by overriding the maximize button behavior
        self.bind("<F11>", self.toggle_fullscreen)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Scrollable frame
        self.grid_rowconfigure(0, weight=1)      # For tab view
        self.grid_rowconfigure(1, weight=0)      # For additional content if needed

        # Create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="SpotiScrape", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create sidebar buttons
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Convert to CSV")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Convert to XLSX")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event, text="Recalculate Analysis")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

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

        # Configure the tabview to stretch
        self.scrollable_frame.grid_rowconfigure(0, weight=1)  # Make the tabview stretch vertically

        self.tabview.add("Current Week")
        self.tabview.add("Prediction: Next Week")
        self.tabview.add("Prediction: Next Month")

        # Create content for each tab
        self.create_tab_content(self.tabview.tab("Current Week"), "Initial data for Current Week")
        self.create_tab_content(self.tabview.tab("Prediction: Next Week"), "Initial data for Prediction Next Week")
        self.create_tab_content(self.tabview.tab("Prediction: Next Month"), "Initial data for Prediction Next Month")

        # Set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

    def toggle_fullscreen(self, event=None):
        # This method does nothing, effectively disabling fullscreen
        pass

    def create_tab_content(self, tab, initial_text=""):
        # Create a frame to hold the canvas and textbox
        content_frame = customtkinter.CTkFrame(tab)
        content_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")

        # Create a canvas for the chart
        self.chart_frame = customtkinter.CTkFrame(content_frame)
        self.chart_frame.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="nsew")

        # Example of creating a Matplotlib figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])  # Replace this with your actual data

        # Create a FigureCanvasTkAgg to embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")  # Use grid here

        # Create a frame for the textbox and scrollbar
        textbox_frame = customtkinter.CTkFrame(content_frame)
        textbox_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")
        textbox_frame.grid_rowconfigure(0, weight=1)  # Allow the textbox to expand
        textbox_frame.grid_columnconfigure(0, weight=1)  # Allow the scrollbar to expand

        # Create a text box within the frame
        self.textbox = customtkinter.CTkTextbox(textbox_frame, state="normal")
        self.textbox.grid(row=0, column=0, padx=(0, 5), pady=(0, 0), sticky="nsew")  # Use sticky for expansion

        # Create a scrollbar linked to the textbox
        self.scrollbar = customtkinter.CTkScrollbar(textbox_frame, orientation="vertical", command=self.textbox.yview)
        self.scrollbar.grid(row=0, column=1, padx=(5, 0), pady=(0, 0), sticky="ns")  # Sticky for vertical scrollbar
        self.textbox.configure(yscrollcommand=self.scrollbar.set)  # Link scrollbar to textbox

        self.textbox.insert("0.0", initial_text)
        self.textbox.configure(state="disabled")  # Make it read-only

    def update_textbox(self, new_text):
        self.textbox.configure(state="normal")  # Enable editing to update
        self.textbox.delete("0.0", "end")  # Clear the text box
        self.textbox.insert("0.0", new_text)  # Insert new data
        self.textbox.configure(state="disabled")  # Make it read-only again

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("Sidebar button clicked")

if __name__ == "__main__":
    app = App()
    app.mainloop()