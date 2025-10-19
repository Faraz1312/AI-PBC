# core_state.py - Persistent Memory and State Manager

import json
import os
import time

# --- Configuration ---
STATE_FILE_PATH = "user_state.json"

DEFAULT_STATE = {
    "last_activity": 0.0,
    "last_lesson": "",
    "lesson_index": 0,
    "current_mode": "main_menu",
    "conversation_history": []
}

def load_state():
    """Loads the application state from the JSON file."""
    try:
        if os.path.exists(STATE_FILE_PATH):
            with open(STATE_FILE_PATH, 'r') as f:
                state = json.load(f)
                # Ensure all default keys exist in the loaded state
                return {**DEFAULT_STATE, **state}
        return DEFAULT_STATE.copy()
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"[STATE ERROR] Corrupted state file, resetting to default. Error: {e}")
        return DEFAULT_STATE.copy()

def save_state(**kwargs):
    """
    Saves the application state, accepting keyword arguments for flexible updates.
    """
    try:
        state = load_state() 
        state["last_activity"] = time.time()
        
        for key, value in kwargs.items():
            # Only update keys that are defined in the default state
            if key in DEFAULT_STATE: 
                state[key] = value
            
        with open(STATE_FILE_PATH, 'w') as f:
            json.dump(state, f, indent=4)
        return True
    except Exception as e:
        print(f"[STATE ERROR] Failed to save state: {e}")
        return False

def reset_lesson_progress():
    """Resets only the lesson progress keys."""
    save_state(last_lesson="", lesson_index=0)