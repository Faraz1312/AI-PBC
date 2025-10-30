# feature_lesson.py - Lesson Module Logic

import os
from core_speech import speak_text, transcribe_audio
from core_llm import get_llm_response
from core_state import load_state, save_state, reset_lesson_progress
import time 

def load_file_lines(folder, filename, config):
    """Loads and strips non-empty lines from the specified lesson file."""
    try:
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            # Reads one natural sentence/segment per list item
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        speak_text("Sorry, that lesson file was not found.", config)
        return []

def wait_for_next(current_line, previous_line, config):
    """Waits for and processes user commands during a lesson segment."""
    while True:
        command = transcribe_audio(config).lower().strip(". ")
        
        # Accept 'next', 'ok', or 'okay' to advance the lesson
        if any(w in command for w in ["next", "okay", "ok"]): 
            return 1
            
        elif "repeat" in command:
            speak_text(current_line, config)
            
        elif "go back" in command and previous_line:
            speak_text("Going back.", config)
            speak_text(previous_line, config)
            return -1
            
        elif "skip" in command:
            return 1
            
        elif "exit" in command:
            return 0
            
        elif "help" in command:
            speak_text("Say: next, repeat, go back, skip, explain more, or exit.", config)
            
        elif "explain more" in command:
            # Use GPT-3.5 to elaborate on the last spoken line
            response = get_llm_response(f"Explain in detail: {current_line}", config)
            speak_text(response, config)
            
        else:
            speak_text("Say: next, repeat, or explain more.", config)

def run_lesson_module(config, lesson_choice=None, start_index=0):
    """
    Main function to run an interactive lesson.
    Handles lesson selection, state management, and line-by-line reading.
    """
    
    lesson_map = {
        "math basics": "math_basics.txt",
        "real numbers": "real_numbers.txt",
        "daily reasoning": "daily_reasoning.txt"
    }
    
    # 1. Handle Lesson Selection (via Intent slot or voice prompt)
    if not lesson_choice or lesson_choice.lower() not in lesson_map:
        speak_text("Which lesson? Say math basics, real numbers, or daily reasoning.", config)
        lesson_choice = transcribe_audio(config).lower().strip(". ")
        if not lesson_choice or lesson_choice.lower() not in lesson_map:
            speak_text("No valid lesson was chosen. Returning to main menu.", config)
            return

    filename = lesson_map.get(lesson_choice.lower())
    
    if not filename:
        speak_text(f"I didn't catch {lesson_choice} or that lesson name.", config)
        return

    lines = load_file_lines("lessons", filename, config)
    
    # 2. Initialization and Resuming State
    i = start_index 
    previous_text = ""
    
    if i > 0:
        speak_text(f"Resuming lesson: {lesson_choice}.", config)

    # 3. Main Lesson Loop (Reads one line at a time)
    while i < len(lines):
        current_line = lines[i]
        
        speak_text(current_line, config)
        
        # Wait for command and get result (1=next, -1=back, 0=exit)
        result = wait_for_next(current_line, previous_text, config)
        
        # 4. State Management and Index Update
        if result == 1:
            # Advance one line (next/ok/skip)
            previous_text, i = current_line, i + 1
            save_state(last_lesson=lesson_choice, lesson_index=i, current_mode="lesson")
        elif result == -1:
            # Go back one line (go back)
            # Ensure index doesn't go below zero
            previous_text, i = current_line, max(0, i - 1)
            save_state(last_lesson=lesson_choice, lesson_index=i, current_mode="lesson")
        elif result == 0:
            # Exit: Save current position before breaking
            save_state(last_lesson=lesson_choice, lesson_index=i, current_mode="lesson")
            break
        else:
            # Fail-safe advance
            i += 1 
            
    # 5. Lesson Completion
    if i >= len(lines):
        speak_text(f"Lesson {lesson_choice} complete! Progress cleared.", config)
        reset_lesson_progress()
