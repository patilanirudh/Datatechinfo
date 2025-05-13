# 📦 Import required libraries
import sounddevice as sd  # For capturing audio input from the microphone
import numpy as np        # For numerical operations and handling audio arrays
import whisper            # OpenAI Whisper model for speech recognition/transcription
import io                 # To work with in-memory byte streams
import scipy.io.wavfile as wav  # For reading and writing WAV audio files
from googletrans import Translator  # For translating text using Google Translate
from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS  
# For converting Indian scripts (like Hindi) to Romanized (English letter) form

# 🎙️ Load the Whisper model
model = whisper.load_model("base")  # Load the lightweight Whisper speech-to-text model

# 🎚️ Configure audio recording settings
samplerate = 16000  # Sample rate in Hz; Whisper expects 16000 samples/sec
channels = 1        # Mono channel (1 mic)
dtype = 'int16'     # 16-bit PCM format (standard format for audio)

# 🌍 Define language options with their codes used by Google Translate
language_options = {
    "1": ("Hindi", "hi"),
    "2": ("Marathi", "mr"),
    "3": ("Gujarati", "gu"),
    "4": ("Tamil", "ta"),
    "5": ("Telugu", "te"),
    "6": ("Kannada", "kn"),
    "7": ("Bengali", "bn"),
    "8": ("Urdu", "ur"),
    "9": ("French", "fr"),
    "10": ("Spanish", "es")
}

# 🧾 Show available language choices to user
print("🌐 Choose a language to translate to:")
for key, (name, _) in language_options.items():
    print(f"{key}. {name}")  # Print each option in numbered format

# 📥 Accept user input for language choice
choice = input("Enter the number of your chosen language: ").strip()  # Read input and strip spaces
lang_name, lang_code = language_options.get(choice, ("English", "en"))  # Default to English if invalid input

# 🎤 Prompt the user to begin speaking
print(f"\n🎙️ Speak now. Press Ctrl+C to stop recording and transcribe in {lang_name}...")

# 📦 Create a list to hold recorded audio chunks
recorded_audio = []

# 🔁 Callback function to be called on each audio chunk recorded
def callback(indata, _, __, status):
    if status:  # If there's an error or warning
        print(f"⚠️ Status: {status}")
    recorded_audio.append(indata.copy())  # Save a copy of the audio chunk
# 🎧 Start capturing microphone input
try:
    with sd.InputStream(samplerate=samplerate, channels=channels, dtype=dtype, callback=callback):
        while True:
            sd.sleep(1000)  # Keeps the stream open (wait 1 second repeatedly)
# 🛑 Handle stopping the recording with Ctrl+C
except KeyboardInterrupt:
    print("\n⏹️ Recording stopped. Transcribing...")
    # 🧩 Merge all recorded chunks into a single NumPy array and convert to float32
    audio_np = np.concatenate(recorded_audio, axis=0).astype(np.float32)

    # 🔊 Normalize audio signal to range [-1.0, 1.0]
    audio_np /= np.max(np.abs(audio_np))
    # 💾 Save the audio to an in-memory buffer instead of disk
    audio_buffer = io.BytesIO()
    wav.write(audio_buffer, samplerate, audio_np)  # Write to buffer in WAV format
    audio_buffer.seek(0)  # Move pointer to beginning of buffer
    # 📤 Read the audio back from the buffer and normalize again
    _, audio_data = wav.read(audio_buffer)  # Read audio (sample rate, data)
    audio_data = audio_data.astype(np.float32)  # Convert to float32
    audio_data /= np.max(np.abs(audio_data))    # Normalize again
    # 🧠 Transcribe speech to text using Whisper
    result = model.transcribe(audio_data)
    original_text = result['text']  # Extract the text
    # 📄 Print the recognized speech
    print("\n📄 Final Transcription:\n")
    print(original_text)
    # 🌍 Translate text to selected language using Google Translate
    translator = Translator()
    translated = translator.translate(original_text, src='en', dest=lang_code)
    # 🗣️ Show the translated text in the native script
    print(f"\n🗣️ Translated Text in {lang_name}:\n{translated.text}")
    # 🔡 If Devanagari-based language, transliterate to Roman letters
    if lang_code in ['hi', 'mr', 'ne', 'sa']:  # Supported for transliteration
        romanized = transliterate(translated.text, DEVANAGARI, ITRANS)
        print(f"\n🔡 Romanized ({lang_name} in English letters):\n{romanized}")
    else:
        print(f"\n⚠️ Romanization not supported for {lang_name}. Showing native script.")
    # 🧹 Clear memory used by audio chunks
    recorded_audio.clear()

