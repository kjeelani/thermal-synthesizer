import numpy as np
import scipy.signal as signal
import soundfile as sf
import pygame
from typing import Optional

# Global variable for the audio object
pygame.mixer.init(frequency=44100, buffer=4096)
pygame.mixer.set_num_channels(32)


class AudioSettings:
    def __init__(
        self,
        lab_type: int,
        resistance: Optional[float] = None,
        capacitance: Optional[float] = None,
        inductance: Optional[float] = None,
        temperature: Optional[float] = None,
        selected_audio: str = "",
    ):
        self.lab_type = lab_type
        self.resistance = resistance
        self.capacitance = capacitance
        self.inductance = inductance
        self.temperature = temperature
        self.selected_audio = selected_audio


# This actually plays the audio_data
def play_audio_with_pygame(audio_data, samplerate, allow_overlap=False):

    # Ensure the audio array is 2D (mono -> stereo if needed)
    if audio_data.ndim == 1:  # Mono sound
        audio_data = np.stack((audio_data, audio_data), axis=-1)

    # Convert the array to a pygame sound object and play
    sound = pygame.sndarray.make_sound((audio_data * 32767).astype(np.int16))
    if allow_overlap:
        sound.play()  # Play sound without stopping others
    else:
        sound.play(loops=0)  # Play sound and stop others if already playing
    return sound


# This is an external call from the GUI
def play_audio(settings: AudioSettings, color=None):
    COLOR_TO_FREQUENCY = {
        "Red": 261.63,  # C4
        "Orange": 293.66,  # D4
        "Yellow": 329.63,  # E4
        "Green": 349.23,  # F4
        "Blue": 392.00,  # G4
        "Indigo": 440.00,  # A4
        "Violet": 493.88,  # B4
    }

    # Switch statement to call appropriate lab function
    if settings.lab_type == 0:
        low_pass_filter(settings)
    elif settings.lab_type == 1:
        resonance_filter(settings)
    elif settings.lab_type == 2:
        thermal_synthesizer(settings, COLOR_TO_FREQUENCY[color if color else "Red"])
    else:
        print("Invalid lab type provided.")
        return


def pause_audio():
    pygame.mixer.stop()


# 1. Low Pass Filter (Frequency Control)
def low_pass_filter(settings: AudioSettings):
    # Load audio file
    data, samplerate = sf.read(settings.selected_audio)

    # RC circuit cutoff frequency: f_c = 1 / (2 * pi * R * C)
    resistance = settings.resistance
    capacitance = settings.capacitance
    cutoff_freq = 1 / (2 * np.pi * resistance * capacitance)

    # Apply low-pass filter using SciPy
    b, a = signal.butter(1, cutoff_freq / (samplerate / 2), btype="low")
    filtered_data = signal.lfilter(b, a, data)

    # Play filtered audio
    play_audio_with_pygame(filtered_data, samplerate)


# 2. Resonance Filter (Resonance Lab)
def resonance_filter(settings: AudioSettings):
    # Load audio file
    data, samplerate = sf.read(settings.selected_audio)

    # LC resonance frequency: f_res = 1 / (2 * pi * sqrt(L * C))
    inductance = settings.inductance
    capacitance = settings.capacitance
    resonance_freq = 1 / (2 * np.pi * np.sqrt(inductance * capacitance))

    if resonance_freq < 20 or resonance_freq > samplerate / 2:
        print(
            f"Error: Resonance frequency {resonance_freq:.2f} Hz is out of audible range."
        )
        return

    # Apply band-pass filter around resonance frequency
    bandwidth = resonance_freq / 10  # Adjust bandwidth to emphasize resonance
    low_cutoff = resonance_freq - bandwidth
    high_cutoff = resonance_freq + bandwidth

    b, a = signal.butter(
        2, [low_cutoff / (samplerate / 2), high_cutoff / (samplerate / 2)], btype="band"
    )
    filtered_data = signal.lfilter(b, a, data)

    if low_cutoff >= high_cutoff:
        print(
            f"Error: Invalid cutoff frequencies. Low: {low_cutoff} Hz, High: {high_cutoff} Hz"
        )
        return

    # Play filtered audio
    play_audio_with_pygame(filtered_data, samplerate)


# 3. Thermal Synthesizer (Thermal Effects Lab)
def thermal_synthesizer(settings: AudioSettings, frequency):
    # Constants for thermal calculation
    print(settings.capacitance, settings.resistance, settings.inductance, frequency)
    R0 = settings.resistance  # Base resistance in ohms
    L = settings.inductance  # Inductance in henries
    C = settings.capacitance  # Capacitance in farads
    alpha = 0.004  # Temperature coefficient for resistance

    # Calculate resistance based on temperature
    temperature = settings.temperature
    resistance = R0 * (1 + alpha * temperature)

    # Calculate resonance frequency and damping
    resonance_freq = 1 / (2 * np.pi * np.sqrt(L * C))  # Resonance frequency
    damping_factor = resistance / (2 * L)  # Energy loss per oscillation
    bandwidth = resonance_freq / 10  # Bandwidth for resonance effect

    # Calculate resonance effect based on input frequency
    resonance_effect = 1 / (1 + ((frequency - resonance_freq) / bandwidth) ** 2)

    samplerate = 44100  # Standard audio sampling rate
    duration = 4  # Duration of sound in seconds
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)

    # Generate damped oscillation with resonance effect
    amplitude = (
        np.exp(-damping_factor * t) * resonance_effect
    )  # Decay envelope with resonance
    oscillation = np.sin(2 * np.pi * frequency * t)  # Input frequency tone
    synthetic_sound = amplitude * oscillation  # Damped and modulated sound

    # Play the generated sound
    play_audio_with_pygame(synthetic_sound, samplerate, allow_overlap=True)
