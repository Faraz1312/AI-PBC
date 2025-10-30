import azure.cognitiveservices.speech as speechsdk
import openai
import os
import smtplib
from email.message import EmailMessage
from config import *
from audio_notes import create_note, list_notes, read_note
# --- ADDED FOR LOGGING AND TIME DELAY FIX ---
import time
import datetime
# ---------------------------------------------

# ---------------- LOGGING UTILITY ----------------
LOG_FILE_PATH = "ai2pbc_log.txt"

def log_message(message, level="INFO"):
    """Writes a time-stamped message to the centralized log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # Also print to console for immediate visibility (will be captured by .sh script)
    print(log_entry.strip()) 
    
    try:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"FATAL: Could not write to log file: {e}")

# ---------------- Fun Facts ----------------
fun_facts = [
    "Beethoven composed some of his best music after going deaf.",
    "Louis Braille invented Braille when he was just 15 years old.",
    "Some blind people use echolocation — like bats — by clicking their tongues.",
    "Guide dogs are trained to disobey unsafe commands — it’s called intelligent disobedience.",
    "There’s a Rubik’s Cube for the blind — it has different textures on each side.",
    "NASA has created tactile star maps so you can feel constellations.",
    "Chess boards for the blind use notches and raised pieces to tell color and position.",
]

# ---------------- Utils ----------------
def speak_text(text):
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = "en-IN-AaravNeural"
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)


    ssml = f"""
    <speak version='1.0' xml:lang='en-IN'>
        <voice name='en-IN-AaravNeural'>
            <prosody rate='+10%'>{text}</prosody>
        </voice>
    </speak>
    """
    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        log_message("TTS failed.", level="ERROR")

def transcribe_audio():
    try:
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
        speech_config.speech_recognition_language = "en-IN"
        audio_config = speechsdk.AudioConfig(use_default_microphone=True)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "4000")
        result = recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.NoMatch:
            log_message("STT NoMatch: No speech detected.", level="DEBUG")
            return ""
        
        return result.text.strip() if result.reason == speechsdk.ResultReason.RecognizedSpeech else ""
    except Exception as e:
        log_message(f"STT error: {e}", level="ERROR")
        return ""

def get_llm_response(prompt):
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are AI Square PBC, an AI Mentoring Platform for blind children, designed and built by Faraz Hasan Khan. You help blind children by teaching them interactively and thus fighting against educational inequality."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log_message(f"LLM error: {e}", level="ERROR")
        return "Sorry, something went wrong with the AI."

def load_file_lines(folder, filename):
    try:
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        speak_text("Sorry, that file was not found.")
        log_message(f"File not found: {os.path.join(folder, filename)}", level="ERROR")
        return []

# ---------------- Flow Helpers ----------------
def wait_for_next(current_line, previous_line=""):
    while True:
        command = transcribe_audio().lower().strip(". ")
        if "next" in command:
            return 1
        elif "repeat" in command:
            speak_text(current_line)
        elif "go back" in command and previous_line:
            speak_text("Going back.")
            speak_text(previous_line)
            return -1
        elif "skip" in command:
            return 1
        elif "exit" in command:
            return 0
        elif "help" in command:
            speak_text("Say: next, repeat, go back, skip, explain more, or exit.")
        elif "explain more" in command:
            speak_text(get_llm_response(f"Explain in detail: {current_line}"))
        else:
            speak_text("Say: next, repeat, or explain more.")

# ---------------- Lesson ----------------
def run_lesson_module():
    log_message("Starting Lesson module.")
    speak_text("Which lesson? Say math basics, real numbers, or daily reasoning.")
    lesson_map = {
        "math basics": "math_basics.txt",
        "real numbers": "real_numbers.txt",
        "daily reasoning": "daily_reasoning.txt"
    }
    choice = transcribe_audio().lower().strip(". ")
    filename = lesson_map.get(choice)
    if filename:
        lines = load_file_lines("lessons", filename)
        i, previous_text = 0, ""
        while i < len(lines):
            line1 = lines[i]
            line2 = lines[i + 1] if i + 1 < len(lines) else ""
            combined = f"{line1} {line2}".strip()
            speak_text(combined)
            result = wait_for_next(combined, previous_text)
            if result == 1:
                previous_text, i = combined, i + 2
            elif result == -1:
                i = max(0, i - 2)
            elif result == 0:
                break
            else:
                i += 2
        log_message(f"Lesson module finished. Lines read: {i}", level="INFO")
    else:
        speak_text("I didn't catch that lesson name.")

# ---------------- Mentor ----------------
def run_mentor_module():
    log_message("Starting Mentor module.")
    speak_text("What do you need help with?")
    q = transcribe_audio()
    response = get_llm_response(q)
    for s in response.split(". "):
        speak_text(s.strip() + ("" if s.strip().endswith(".") else "."))
        if wait_for_next(s.strip()) == 0:
            break
    log_message("Mentor module finished.")

# ---------------- Talk ----------------
# ---------- Talk Mode ----------
def run_talk_mode():
    log_message("Starting Talk module.")
    speak_text("Let's chat! What's on your mind?")
    while True:
        user_input = transcribe_audio()
        if not user_input:
            speak_text("I didn’t catch that. Please say something.")
            continue

        # Exit if user wants to stop talking
        if any(word in user_input.lower() for word in ["exit", "stop", "back", "go back", "main menu"]):
            speak_text("Okay, exiting talk mode.")
            log_message("Exiting Talk module by user command.")
            break

        # Get LLM response and speak full response at once
        response = get_llm_response(user_input)
        speak_text(response)
        speak_text("What else would you like to talk about?")
# ---------------- Fun ----------------
def run_fun_fact_module():
    import random
    log_message("Executing Fun Fact module.")
    speak_text("Here’s a fun fact.")
    speak_text(random.choice(fun_facts))

# ---------------- Test ----------------
def run_test_module():
    log_message("Starting Test module.")
    speak_text("Which test would you like to take?")
    subject = transcribe_audio().lower().strip(". ")
    filename = subject.replace(" ", "_") + "_test.txt"
    questions = load_file_lines("tests", filename)

    score, total = 0, 0
    qna_pairs = []

    for i in range(0, len(questions), 2):
        if questions[i].startswith("Q:") and questions[i + 1].startswith("A:"):
            q = questions[i][2:].strip()
            a = questions[i + 1][2:].strip().lower()
            total += 1

            speak_text(f"Question {total}: {q}")
            answer = transcribe_audio().lower()
            correct = a in answer
            speak_text("Correct!" if correct else "Incorrect.")
            score += int(correct)
            qna_pairs.append((q, answer, a, correct))

    report = f"Test: {subject}\nScore: {score}/{total}\n\n"
    for i, (q, user_ans, correct_ans, status) in enumerate(qna_pairs, 1):
        report += f"{i}. {q}\nYour Answer: {user_ans}\nCorrect Answer: {correct_ans}\nResult: {'' if status else ''}\n\n"

    report_path = f"reports/{subject.replace(' ', '_')}_report.txt"
    os.makedirs("reports", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    speak_text(f"You scored {score} out of {total}. Report saved.")
    send_email_report(subject, report_path)
    log_message(f"Test module finished. Score: {score}/{total}", level="INFO")

# ---------------- Email ----------------
def send_email_report(subject, filepath):
    msg = EmailMessage()
    msg["Subject"] = f"AI2PBC Test Report: {subject}"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GUARDIAN_EMAIL
    with open(filepath, "r", encoding="utf-8") as f:
        msg.set_content(f.read())
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        log_message("Email sent successfully.")
    except Exception as e:
        log_message(f"Email failed: {e}", level="ERROR")

# ---------------- My Performance ----------------
def run_my_performance():
    log_message("Starting Performance module.")
    files = os.listdir("reports")
    if not files:
        speak_text("No performance reports found.")
        log_message("No performance reports found.")
    else:
        latest = sorted(files)[-1]
        with open(f"reports/{latest}", "r", encoding="utf-8") as f:
            for line in f:
                speak_text(line.strip())
        log_message(f"Latest report read: {latest}", level="INFO")

# ---------------- Notes ----------------
def run_notes_module():
    log_message("Starting Notes module.")
    speak_text("Welcome to notes. Say create a note, read existing notes, or exit.")
    while True:
        action = transcribe_audio().lower()
        if "create" in action or "make" in action or "new note" in action:
            create_note()
            log_message("Note creation initiated.")
        elif "read" in action or "existing" in action or "listen" in action:
            notes = list_notes()
            if not notes:
                speak_text("You have no saved notes.")
                log_message("Attempted to read notes, but none were found.")
                # We should break or return here to prevent infinite loop of reading notes.
                break 
            speak_text("Here are your notes:")
            for note in notes:
                speak_text(note.replace("_", " "))
            speak_text("Say the name of the note you want to hear.")
            name = transcribe_audio().strip().lower().replace(" ", "_")
            read_note(name)
            log_message(f"Attempted to read note: {name}")
        elif "exit" in action or "back" in action:
            speak_text("Exiting notes.")
            log_message("Exiting Notes module.")
            return
        else:
            speak_text("Please say create, read, or exit.")

# ---------------- Mode Selector ----------------
def get_mode(text):
    import string
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    if "learn" in text:
        return "lesson"
    elif "mentor" in text or "doubt" in text or "support" in text:
        return "mentor"
    elif "fun" in text or "fact" in text:
        return "fun"
    elif "talk" in text:
        return "talk"
    elif "test" in text:
        return "test"
    elif "note" in text:
        return "notes"
    elif "performance" in text:
        return "performance"
    elif "exit" in text or "quit" in text:
        return "exit"
    else:
        return "unknown"

# ---------------- Main Loop ----------------
def main():
    log_message("Application starting...", level="INFO")
    speak_text("Hello! I am your AI companion. Say Learn, Doubts, Talk, Fun, Test, My Notes, or My Performance.")
    
    try:
        while True:
            # Added for system stability
            time.sleep(0.5)
            
            user_text = transcribe_audio()
            if not user_text:
                speak_text("I didn't hear you. Say Learn, Doubts, Talk, Fun, Test, My Notes, or My Performance.")
                continue

            log_message(f"User Input: {user_text}", level="USER")
            
            mode = get_mode(user_text)
            log_message(f"Mode Detected: {mode}", level="INFO")
            
            if mode == "lesson":
                run_lesson_module()
            elif mode == "mentor":
                run_mentor_module()
            elif mode == "talk":
                run_talk_mode()
            elif mode == "fun":
                run_fun_fact_module()
            elif mode == "test":
                run_test_module()
            elif mode == "notes":
                run_notes_module()
            elif mode == "performance":
                run_my_performance()
            elif mode == "exit":
                speak_text("Goodbye! Exiting now.")
                log_message("Application exiting by user command.", level="INFO")
                break
            else:
                speak_text("Say Learn, Doubts, Talk, Fun, Test, My Notes, or My Performance.")

    except KeyboardInterrupt:
        log_message("Application interrupted by Ctrl+C.", level="INFO")
    except Exception as e:
        log_message(f"CRITICAL ERROR in main loop: {e}", level="FATAL")

if __name__ == "__main__":
    # Ensure all necessary folders exist before starting
    for folder in ["lessons", "notes", "reports", "tests"]:
        os.makedirs(folder, exist_ok=True)
    main()
