# core_speech.py - AZURE Speech-to-Text and Text-to-Speech Core (ONLINE ONLY)

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import ResultReason

# ---------------- AZURE TTS ----------------

def speak_text(text, config):
    """Uses Azure TTS to convert text to speech."""
    try:
        speech_config = speechsdk.SpeechConfig(subscription=config.AZURE_SPEECH_KEY, region=config.AZURE_SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = "en-IN-AaravNeural"
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        # Use SSML to increase speaking speed
        ssml = f"""
        <speak version='1.0' xml:lang='en-IN'>
            <voice name='en-IN-AaravNeural'>
                <prosody rate='+10%'>{text}</prosody>
            </voice>
        </speak>
        """
        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            if result.error_details:
                print(f"[AZURE TTS failed]: {result.error_details}")
            else:
                print("[AZURE TTS failed for unknown reason.]")
    except Exception as e:
        print(f" TTS error: {e}")


# ---------------- AZURE STT ----------------

def transcribe_audio(config):
    """Uses Azure STT to capture and transcribe user audio with robust VAD."""
    try:
        speech_config = speechsdk.SpeechConfig(subscription=config.AZURE_SPEECH_KEY, region=config.AZURE_SPEECH_REGION)
        speech_config.speech_recognition_language = "en-IN"
        audio_config = speechsdk.AudioConfig(use_default_microphone=True)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # Robust VAD settings (4000ms initial silence)
        recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "4000")
        
        print("[AZURE STT] Listening...")
        result = recognizer.recognize_once_async().get()
        
        if result.reason == ResultReason.RecognizedSpeech:
            return result.text.strip()
        
        if result.reason == ResultReason.NoMatch:
             print(" No speech detected.")
             return ""

        return ""
    except Exception as e:
        print(f" STT error: {e}")
        return ""