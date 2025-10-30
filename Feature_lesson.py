# feature_lesson.py - Lesson Module Logic

import os
from core_speech import speak_text, transcribe_audio
from core_llm import get_llm_response
from core_state import load_state, save_state, reset_lesson_progress
import time 

def load_file_lines(folder, filename, config):
    try:
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            # We preserve the list of lines as is
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        speak_text("Sorry, that file was not found.", config)
        return []

def wait_for_next(current_line, previous_line, config):
    # This function remains efficient and unchanged, receiving only the line just spoken.
    while True:
        command = transcribe_audio(config).lower().strip(". ")
        if any(w in command for w in ["next", "okay", "ok"]): # Added common user confirmations
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
            response = get_llm_response(f"Explain in detail: {current_line}", config)
            speak_text(response, config)
        else:
            speak_text("Say: next, repeat, or explain more.", config)

def run_lesson_module(config, lesson_choice=None, start_index=0):
    
    lesson_map = {
        "math basics": "math_basics.txt",
        "real numbers": "real_numbers.txt",
        "daily reasoning": "daily_reasoning.txt"
    }
    
    if not lesson_choice or lesson_choice.lower() not in lesson_map:
        speak_text("Which lesson? Say math basics, real numbers, or daily reasoning.", config)
        lesson_choice = transcribe_audio(config).lower().strip(". ")
        if not lesson_choice or lesson_choice.lower() not in lesson_map:
            speak_text("No lesson was chosen. Returning to main menu.", config)
            return

    filename = lesson_map.get(lesson_choice.lower())
    
    if not filename:
        speak_text(f"I didn't catch {lesson_choice} or that lesson name.", config)
        return

    lines = load_file_lines("lessons", filename, config)
    
    i = start_index 
    previous_text = ""
    
    # *** CRITICAL CHANGE: The index no longer needs to ensure it's on an even number ***
    # Now, if we resume from an odd index, we just start there.
    # We only check if we need to announce resuming.
    if i > 0:
        speak_text(f"Resuming lesson: {lesson_choice}.", config)

    while i < len(lines):
        # 3. Read lesson content - SPEAK ONLY ONE LINE
        current_line = lines[i]
        
        speak_text(current_line, config)
        
        # 4. Wait for user command and manage state
        # We pass the single line spoken as the 'current_line'
        result = wait_for_next(current_line, previous_text, config)
        
        if result == 1:
            # Advance one line, save state with the new index
            previous_text, i = current_line, i + 1
            save_state(last_lesson=lesson_choice, lesson_index=i, current_mode="lesson")
        elif result == -1:
            # Go back one line (i - 1), save state with the new index
            previous_text, i = current_line, max(0, i - 1)
            save_state(last_lesson=lesson_choice, lesson_index=i, current_mode="lesson")
        elif result == 0:
            # Exit: Save current position before breaking
            save_state(last_lesson=lesson_choice, lesson_index=i, current_mode="lesson")
            break
        else:
            # Should not happen, but prevents infinite loop/skips ahead by 1
            i += 1 
            
    if i >= len(lines):
        speak_text(f"Lesson {lesson_choice} complete! Progress cleared.", config)
        reset_lesson_progress()
