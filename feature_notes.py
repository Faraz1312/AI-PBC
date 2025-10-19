# feature_notes.py - Notes Module Logic

import os
from core_speech import speak_text, transcribe_audio
# NOTE: Assumes audio_notes.py is available in the main directory
from audio_notes import create_note, list_notes, read_note 

def run_notes_module(config, note_name_slot=None):
    
    # 1. Direct Access from AI Intent (The Brain feature)
    if note_name_slot and note_name_slot not in ["create a note", "new note"]:
        name = note_name_slot.strip().lower().replace(" ", "_")
        
        try:
            # Check if the note exists (must list all files in lowercase for case-insensitive check)
            if name + ".txt" in [f.lower() for f in os.listdir("notes")]:
                speak_text(f"Opening note: {note_name_slot}", config)
                read_note(name)
                return 
            else:
                speak_text(f"Sorry, I could not find a note named {note_name_slot}", config)
        except FileNotFoundError:
            speak_text("Notes folder not found. Cannot proceed.", config)
            return

    # 2. Interactive Menu (Original Logic)
    speak_text("Welcome to notes. Say create a note, read existing notes, or exit.", config)
    while True:
        # If AI intent was notes_create, action is pre-filled
        action = transcribe_audio(config).lower()
        
        if "create" in action or "make" in action or "new note" in action:
            create_note()
        
        elif "read" in action or "existing" in action or "listen" in action:
            notes = list_notes()
            if not notes:
                speak_text("You have no saved notes.", config)
                continue
            
            speak_text("Here are your notes:", config)
            for note in notes:
                speak_text(note.replace("_", " "), config)
            
            speak_text("Say the name of the note you want to hear.", config)
            name = transcribe_audio(config).strip().lower().replace(" ", "_")
            read_note(name)

        elif "exit" in action or "back" in action:
            speak_text("Exiting notes.", config)
            return
        
        else:
            speak_text("Please say create, read, or exit.", config)