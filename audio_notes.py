import os
import time
from utils_speech import speak_text, transcribe_audio

NOTES_DIR = "notes"

# Ensure notes directory exists
def ensure_notes_dir():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

# Create a new voice note
def create_note():
    ensure_notes_dir()
    speak_text("What should I name this note?")
    name = transcribe_audio().strip().lower().replace(" ", "_")

    if not name:
        speak_text("I didn't catch the name. Please try again later.")
        return

    filename = f"{NOTES_DIR}/{name}.txt"
    speak_text("Okay, start speaking your note after the beep.")
    time.sleep(1)

    speak_text("Listening...")
    content = transcribe_audio()

    if content:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        speak_text("Your note has been saved successfully.")
    else:
        speak_text("I didn't hear anything. Note not saved.")

# List notes sorted by latest modified
def list_notes():
    files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(NOTES_DIR, f)), reverse=True)
    return [f[:-4] for f in files]

# Read a selected note aloud
def read_note(note_name=None):
    files = list_notes()
    
    if not files:
        speak_text("You have no saved notes yet.")
        return

    if not note_name:
        speak_text("Here are your notes:")
        for f in files:
            # Say note name clearly, with slight pause
            speak_text(f.replace("_", " "))
            time.sleep(0.5)

        speak_text("Which note would you like me to read?")
        note_name = transcribe_audio().strip().lower().replace(" ", "_")

    filename = f"{NOTES_DIR}/{note_name}.txt"
    if not os.path.exists(filename):
        speak_text("Sorry, that note was not found.")
        return

    speak_text(f"Reading your note: {note_name.replace('_', ' ')}")
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                speak_text(line.strip())

# My Notes Mode — accessible from main menu
def run_audio_notes_module():
    ensure_notes_dir()
    speak_text("Welcome to your notes. You can say: create a note, read existing notes, or exit.")
    
    while True:
        command = transcribe_audio().lower().strip()
        if "create" in command or "make" in command or "new note" in command:
            create_note()
        elif "read" in command or "existing" in command or "open" in command:
            read_note()
        elif "exit" in command or "back" in command:
            speak_text("Exiting notes.")
            break
        else:
            speak_text("Please say create a note, read existing notes, or exit.")
