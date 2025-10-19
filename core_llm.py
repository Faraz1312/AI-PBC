# core_llm.py - AZURE/GPT Intelligence and Intent Routing Core (ONLINE ONLY)

import openai
import json
# Note: core_speech is imported in main, but we need speak_text for error feedback here.
# Assuming core_speech is importable or functions are passed via config/global context.

# Define all possible Intents and Slots for the LLM Brain
INTENTS = {
    "continue": "Loads the last saved lesson progress.",
    "lesson": "Starts a lesson module. Requires lesson name in slot.",
    "mentor": "Starts the mentor/doubt-solving chat mode.",
    "talk": "Starts the general conversation chat mode.",
    "fun": "Requests a fun fact.",
    "test": "Starts a test module. Requires subject name in slot.",
    "notes_read": "Reads a specific note. Requires note title in slot.",
    "notes_create": "Starts the process to create a new note.",
    "performance": "Checks the latest test report.",
    "exit": "Shuts down the application.",
    "unknown": "Intent could not be classified or is off-topic."
}

def get_llm_response(prompt, config):
    """
    GPT-3.5: Used for general Q&A, Mentor Mode, and Explain More logic.
    """
    system_prompt = "You are AI Square PBC, an AI Mentoring Platform for blind children, designed and built by Faraz Hasan Khan. You help blind children by teaching them interactively and thus fighting against educational inequality. Be concise."
    
    try:
        openai.api_key = config.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f" LLM error (GPT-3.5 Q&A): {e}.")
        return "Sorry, I can't connect to my brain right now."

def get_ai_intent(user_text, config):
    """
    GPT-3.5: Used for Intent Routing. Forces structured JSON output.
    """
    
    # 1. Construct the constrained, JSON-forced prompt
    intent_list = ", ".join(f"'{k}': {v}" for k, v in INTENTS.items())
    
    # System prompt enforcing the structured output
    router_system_prompt = f"""
    You are an expert intent classifier. Your task is to analyze the user's request and classify it into one of the following intents.
    Your output MUST be a single JSON object with two keys: "intent" and "slot".
    
    AVAILABLE INTENTS: {intent_list}
    
    - 'intent': The best matching intent from the list above (e.g., 'lesson').
    - 'slot': A detailed, lowercase string extracted from the user's query relevant to the intent (e.g., 'real numbers', or empty string if not applicable).
    
    User Query: "{user_text}"
    """
    
    # 2. Call the LLM with the JSON constraint
    try:
        openai.api_key = config.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": router_system_prompt}
            ],
            temperature=0.0, # Set to 0 for deterministic output (CRITICAL for JSON)
        )
        llm_output_text = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"[AI INTENT ERROR] GPT-3.5 call failed: {e}. Falling back to keyword matching.")
        return {"intent": "fallback", "slot": user_text}

    # 3. Parse the JSON response
    try:
        # Clean up and extract the JSON object (handling markdown wrappers)
        json_str = llm_output_text.strip()
        if json_str.startswith('```json'):
            json_str = json_str.split('```json')[1].split('```')[0].strip()
        
        intent_data = json.loads(json_str)
        
        # 4. Validate and return the structured data
        if 'intent' in intent_data and intent_data['intent'].lower() in INTENTS:
            return {
                "intent": intent_data['intent'].lower(),
                "slot": intent_data.get('slot', '').lower().strip('. ')
            }
        
        print(f"[AI INTENT] Invalid intent name received: {intent_data.get('intent')}. Output: {llm_output_text}")
        return {"intent": "fallback", "slot": user_text}

    except (json.JSONDecodeError, Exception) as e:
        print(f"[AI INTENT ERROR] Failed to parse LLM output. Fallback to keyword matching. Error: {e}")
        return {"intent": "fallback", "slot": user_text}