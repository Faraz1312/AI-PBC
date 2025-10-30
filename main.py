import azure.cognitiveservices.speech as speechsdk
import openai
import os
import smtplib
from email.message import EmailMessage
from config import * # Load all configuration variables

# --- ADDED FOR FIXES & DEBUGGING ---
import time
import datetime
# -----------------------------------

# --- CORE AI/STATE IMPORTS ---
# Note: You need to import all feature and core files here to make them accessible
from core_speech import speak_text, transcribe_audio 
from core_llm import get_ai_intent, get_llm_response
from core_state import load_state, save_state, reset_lesson_progress
from feature_lesson import run_lesson_module
from feature_notes import run_notes_module
# Assuming audio_notes.py is in the main directory
from audio_notes import create_note, list_notes, read_note 

# ---------------- LOGGING UTILITY ----------------
LOG_FILE_PATH = "ai2pbc_log.txt"

def log_message(message, level="INFO"):
    """Writes a time-stamped message to the centralized log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # Also print to console for immediate visibility
    print(log_entry.strip()) 
    
    try:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        # Note: If this fails, something is fundamentally wrong with the file system.
        print(f"FATAL: Could not write to log file: {e}")

# ---------------- Fun Facts (Unchanged) ----------------
fun_facts = [
    "Beethoven composed some of his best music after going deaf.",
    "Louis Braille invented Braille when he was just 15 years old.",
    "Some blind people use echolocation — like bats — by clicking their tongues.",
    "Guide dogs are trained to disobey unsafe commands — it’s called intelligent disobedience.",
    "There’s a Rubik’s Cube for the blind — it has different textures on each side.",
    "NASA has created tactile star maps so you can feel constellations.",
    "Chess boards for the blind use notches and raised pieces to tell color and position.",
]

# ---------------- Flow Helpers (Removed/Modularized in V3.2) ----------------
# NOTE: Most helper functions were moved to core_speech, core_llm, or feature_lesson.
# The original functions from the old main.py are still listed below 
# but should be removed in your actual file if they are now in core modules.
# We keep the core utility logic (speak_text, transcribe_audio, get_llm_response) simple 
# for the mode-specific functions that remain here. 
# ***NOTE: For the purposes of this complete code, I have replaced the old monolithic functions
# with calls to the new core modules where appropriate.***

# ---------------- Mentor ----------------
def run_mentor_module(config):
    speak_text("What do you need help with?", config)
    q = transcribe_audio(config)
    response = get_llm_response(q, config)
    speak_text(response, config)

# ---------------- Talk ----------------
def run_talk_mode(config):
    speak_text("Let's chat! What's on your mind?", config)
    while True:
        user_input = transcribe_audio(config)
        if not user_input:
            speak_text("I didn’t catch that. Please say something.", config)
            continue

        if any(word in user_input.lower() for word in ["exit", "stop", "back", "go back", "main menu"]):
            speak_text("Okay, exiting talk mode.", config)
            break

        response = get_llm_response(user_input, config)
        speak_text(response, config)
        speak_text("What else would you like to talk about?", config)

# ---------------- Fun ----------------
def run_fun_fact_module(config):
    log_message("Executing Fun Fact module.")
    speak_text("Here’s a fun fact.", config)
    speak_text(random.choice(fun_facts), config)

# ---------------- Test ----------------
def run_test_module(config, subject_slot=None):
    # This is placeholder logic, assuming the detailed logic is not yet modularized.
    speak_text("Test module starting.", config)
    # ... (detailed test logic goes here, or is moved to feature_test.py)
    speak_text("Test module finished.", config)

# ---------------- My Performance ----------------
def run_my_performance(config):
    # This is placeholder logic, assuming the detailed logic is not yet modularized.
    speak_text("Performance report module starting.", config)
    # ... (detailed report logic goes here)
    speak_text("Performance report module finished.", config)


# ---------------- Main Loop (The AI Router) ----------------
def main():
    config = sys.modules[__name__] # Pass the current module as config (contains globals)
    log_message("AI²PBC Application starting...", level="INFO")

    # 1. State Check and Greeting
    state = load_state()
    last_lesson = state.get("last_lesson")
    lesson_index = state.get("lesson_index", 0)
    
    greeting = "Hello! I am your AI companion."
    if last_lesson and lesson_index > 0:
        greeting = f"Welcome back! Your last lesson was {last_lesson}. Say 'continue' or state your command."
    
    speak_text(greeting, config)
    log_message(f"Initial Greeting: {greeting}")
    
    # 2. Main Command Loop
    try:
        while True:
            # Short delay to prevent re-listening immediately after speaking
            time.sleep(0.5) 

            # Listen for command
            user_text = transcribe_audio(config)
            if not user_text:
                log_message("No speech detected. Loop continues.")
                continue

            log_message(f"User Input: {user_text}", level="USER")
            
            # 3. AI Intent Routing
            intent_data = get_ai_intent(user_text, config)
            intent = intent_data.get("intent", "unknown")
            slot = intent_data.get("slot", "")
            
            log_message(f"AI Intent: {intent}, Slot: {slot}")

            if intent == "continue" and last_lesson and lesson_index > 0:
                run_lesson_module(config, lesson_choice=last_lesson, start_index=lesson_index)
            elif intent == "lesson":
                run_lesson_module(config, lesson_choice=slot)
            elif intent == "mentor":
                run_mentor_module(config)
            elif intent == "talk":
                run_talk_mode(config)
            elif intent == "fun":
                run_fun_fact_module(config)
            elif intent == "test":
                run_test_module(config, subject_slot=slot)
            elif intent == "notes_read" or intent == "notes_create":
                run_notes_module(config, note_name_slot=slot)
            elif intent == "performance":
                run_my_performance(config)
            elif intent == "exit":
                speak_text("Goodbye! Exiting now.", config)
                log_message("Application exiting by user command.", level="INFO")
                break
            elif intent == "fallback" or intent == "unknown":
                speak_text("I didn't quite catch that, or that command isn't available yet.", config)
                speak_text("Try saying: Learn, Mentor, Test, or Notes.", config)

    except KeyboardInterrupt:
        log_message("Application interrupted by Ctrl+C.", level="INFO")
    except Exception as e:
        log_message(f"CRITICAL ERROR in main loop: {e}", level="FATAL")

if __name__ == "__main__":
    # Ensure all necessary folders exist before starting
    for folder in ["lessons", "notes", "reports", "tests"]:
        os.makedirs(folder, exist_ok=True)
    
    # The config import needs to happen outside main for the log function to use it.
    main()
