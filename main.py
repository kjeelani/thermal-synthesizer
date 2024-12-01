import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
from processing import AudioSettings, pause_audio, play_audio  # For audio playback

audio_options_to_file = {
    "Violin": "audio/violin.wav",
    "Drum": "audio/drums.wav",
    "Song": "audio/song.mp3",
}


# Function to load images
def load_image(image_path, width=400, height=200):
    img = Image.open(image_path)
    img.resize((width, height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


# Function to create sliders
def create_slider(parent, label, from_, to_, command=None):
    frame = ttk.Frame(parent)
    frame.pack(pady=10, fill="x")
    ttk.Label(frame, text=label).pack(side="left", padx=10)
    slider = ttk.Scale(
        frame, from_=from_, to_=to_, orient="horizontal", command=command
    )
    slider.pack(side="right", expand=True, fill="x", padx=10)
    return slider


def create_number_input(parent, label, default_value, command=None):
    frame = ttk.Frame(parent)
    frame.pack(pady=10, fill="x")
    ttk.Label(frame, text=label).pack(side="left", padx=10)

    # Validation function for numerical input
    def validate_input(value_if_allowed):
        if (
            value_if_allowed == "" or value_if_allowed == "-"
        ):  # Allow empty or negative sign during input
            return True
        try:
            float(value_if_allowed)  # Check if the value can be converted to float
            return True
        except ValueError:
            return False

    # Register validation function
    vcmd = frame.register(validate_input)

    # Create the entry widget with validation
    entry = ttk.Entry(
        frame,
        width=10,
        validate="key",
        validatecommand=(vcmd, "%P"),  # "%P" passes the current value of the entry
    )
    entry.insert(0, str(default_value))  # Set default value
    entry.pack(side="right", padx=10)

    # Add command if provided (triggered when input changes)
    if command:

        def on_value_change(event):
            try:
                value = float(entry.get())
                command(value)  # Pass the updated value to the command
            except ValueError:
                pass  # Ignore invalid inputs

        entry.bind("<FocusOut>", on_value_change)
        entry.bind("<Return>", on_value_change)

    return entry


# Function to create dropdowns
def create_dropdown(parent, label, options, default=0, command=None):
    frame = ttk.Frame(parent)
    frame.pack(pady=10, fill="x")
    ttk.Label(frame, text=label).pack(side="left", padx=10)
    dropdown = ttk.Combobox(frame, values=options, state="readonly")
    dropdown.set(options[default])
    dropdown.pack(side="right", expand=True, fill="x", padx=10)
    dropdown.bind("<<ComboboxSelected>>", command)
    return dropdown


# Function to create buttons
def create_buttons(parent, play_command, pause_command):
    frame = ttk.Frame(parent)
    frame.pack(pady=10)
    play_button = ttk.Button(frame, text="Play", command=play_command)
    play_button.pack(side="left", padx=10)
    pause_button = ttk.Button(frame, text="Pause", command=pause_command)
    pause_button.pack(side="right", padx=10)


def get_audio_settings(lab_type: int, **kwargs) -> AudioSettings:
    return AudioSettings(
        lab_type=lab_type,
        resistance=kwargs.get("resistance"),
        capacitance=kwargs.get("capacitance"),
        inductance=kwargs.get("inductance"),
        temperature=kwargs.get("temperature"),
        selected_audio=kwargs.get("selected_audio"),
    )


# Initialize main GUI
root = tk.Tk()
root.title("Circuit Sound Synthesizer")

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Frequency Control Tab
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Frequency Control")

rc_image = load_image("images/RC.png")
rc_label = tk.Label(tab1, image=rc_image)
rc_label.pack(pady=10)
rc_audio_dropdown = create_dropdown(tab1, "Select Audio", ["Violin", "Drum", "Song"])
rc_r_input = create_number_input(tab1, "Resistance (Ω)", 1000)
rc_c_input = create_number_input(tab1, "Capacitance (μF)", 1)


def play_rc_audio():
    settings = get_audio_settings(
        lab_type=0,
        resistance=float(rc_r_input.get()),
        capacitance=float(rc_c_input.get()) * 1e-6,
        selected_audio=audio_options_to_file[rc_audio_dropdown.get()],
    )
    play_audio(settings)


create_buttons(tab1, play_rc_audio, pause_audio)

# Resonance Tab
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Resonance")

lc_image = load_image("images/LC.jpg")
lc_label = tk.Label(tab2, image=lc_image)
lc_label.pack(pady=10)
lc_audio_dropdown = create_dropdown(tab2, "Select Audio", ["Violin", "Drum", "Song"])
lc_l_input = create_number_input(tab2, "Inductance (mL)", 2.5)
lc_c_input = create_number_input(tab2, "Capacitance (μF)", 1)


def play_lc_audio():
    settings = get_audio_settings(
        lab_type=1,
        inductance=float(lc_l_input.get()) * 1e-3,
        capacitance=float(lc_c_input.get()) * 1e-6,
        selected_audio=audio_options_to_file[lc_audio_dropdown.get()],
    )
    play_audio(settings)


create_buttons(tab2, play_lc_audio, pause_audio)

# Thermal Effects Tab
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Thermal Synthesizer")

# Load RLC image
rlc_image = load_image("images/RLC.png")
rlc_label = tk.Label(tab3, image=rlc_image)
rlc_label.pack(pady=10)

# Create number inputs for Temperature, Resistance, Inductance, and Capacitance
temperature_slider = create_number_input(tab3, "Temperature (C)", 24)
resistance_slider = create_dropdown(
    tab3, "Resistance (Ω)", [".1", "1", "10", "100"], default=1
)
inductance_slider = create_dropdown(
    tab3, "Inductance (H)", [".001", ".01", ".1", "1"], default=1
)
capacitance_slider = create_dropdown(
    tab3, "Capacitance (μF)", [".1", "1", "10", "100"], default=1
)


# Play RLC audio function
def play_rlc_audio(color=None):
    settings = get_audio_settings(
        lab_type=2,
        temperature=float(temperature_slider.get()),
        resistance=float(resistance_slider.get()),
        inductance=float(inductance_slider.get()),
        capacitance=float(capacitance_slider.get()) * 1e-6,  # Convert μF to F
    )
    print(color)
    play_audio(settings, color=color)


rainbow_colors = {
    "Red": "#FF0000",
    "Orange": "#FFA500",
    "Yellow": "#FFFF00",
    "Green": "#008000",
    "Blue": "#0000FF",
    "Indigo": "#4B0082",
    "Violet": "#EE82EE",
}

# Define the key-to-color mapping
key_to_color = {
    "z": "Red",
    "x": "Orange",
    "c": "Yellow",
    "v": "Green",
    "b": "Blue",
    "n": "Indigo",
    "m": "Violet",
}

rainbow_frame = ttk.Frame(tab3)
rainbow_frame.pack(pady=10)

rainbow_frame = ttk.Frame(tab3)
rainbow_frame.pack(pady=10)

# Add Buttons to Play Sounds
button_refs = {}

for color, hex_color in rainbow_colors.items():
    button = tk.Button(
        rainbow_frame,
        text="🎵",
        bg=hex_color,  # Set background color
        fg=(
            "white" if color in ["Red", "Blue", "Indigo"] else "black"
        ),  # Adjust text color for contrast
        command=lambda c=color: play_rlc_audio(c),
    )
    button.pack(side="left", padx=5)

    # Store button reference for each color
    button_refs[color] = button


def keypress(event):
    color = key_to_color.get(event.char.lower())  # Match key to color
    if color and color in button_refs:
        # Simulate button press
        button = button_refs[color]
        button.config(relief="sunken")  # Change style to pressed
        button.invoke()  # Trigger the button's command

        # Restore normal style after a short delay
        root.after(100, lambda: button.config(relief="raised"))


# Add Keybinds
for key in key_to_color.keys():
    root.bind(f"<{key}>", keypress)

# Run the GUI
root.mainloop()
