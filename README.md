# AI²PBC  
**AI-powered Interactive Platform for Blind Children**  

##  Overview  
**AI²PBC** is an affordable, voice-first educational assistant designed to address the learning disadvantages faced by blind and low-vision students, especially in rural and under-resourced areas. Unlike basic screen readers, AI²PBC delivers **personalized learning, smart, conversational navigation, and structured guidance**—all in an accessible, audio-only format.  

Built on a **Raspberry Pi** and powered by **Microsoft Azure Speech Services** and **OpenAI language models**, it uses a highly **modular code architecture** for future offline scalability. AI²PBC is portable, low-cost, and ideal for rural schools, low-income homes, and NGO deployments.  

---

##  Problem Statement  
Millions of blind and visually impaired children lack access to quality education due to:  
- Limited accessibility and rigid interfaces in existing tools.  
- No personalized or structured learning paths.  
- Lack of real-time doubt-solving and meaningful engagement.  
- High cost of commercial solutions.  

---

##  Objectives  
- Deliver a **low-cost, AI-powered tutor** accessible to everyone.  
- Provide **structured audio-based lessons** that adapt to the student.  
- Enable **instant doubt-solving** and complex query handling.  
- Support **skill-building tests** and **personal notes**.  
- Establish a **modular, scalable codebase** ready for feature growth.  

---

##  Core Features (V2.1.0 Update)  
- **AI-Driven Navigation (The "Brain")** – The system eliminates traditional menus. The AI instantly classifies complex voice commands (e.g., "Open my note on World History") and routes directly to the action, drastically improving the user experience.
- **Persistent Memory** – The system automatically saves the user's lesson progress ($\text{lesson name}$ and $\text{line index}$). On restart, the user is greeted and prompted to instantly resume their learning session.
- **Interactive Subject Learning** – Structured lessons with voice flow control (`next`, `repeat`, `explain more`).  
- **AI-Powered Mentorship** – Real-time guidance and motivational support via GPT-3.5.  
- **Verbal Test Mode** – Chapter-wise tests with automated scoring and error analysis.  
- **Performance Reporting** – Auto-generated score reports emailed instantly to guardians.  
- **Audio Notes Mode** – Record, organize, and replay spoken notes with voice-activated retrieval.  

---

##  Technology Stack  
**Hardware:**  
- Raspberry Pi 5  
- Microphone module  
- Bluetooth speaker  
- Waveshare UPS HAT (B)  

**Software:**  
- **Python Modular Core** – Separated into `core_speech`, `core_llm`, and `core_state` for stability.
- **Azure Speech-to-Text & Text-to-Speech** – Provides reliable, high-quality voice I/O.  
- **OpenAI GPT-3.5-turbo** – Powers core intelligence and the **AI Intent Classification** engine.  
- **JSON File Persistence** – Used for saving robust user progress (`user_state.json`).  
- Local `.txt` lesson/test files / Gmail API for automated emails.  

---

##  System Architecture (AI-Driven Flow)  
1. **Input:** Voice command via microphone.  
2. **Processing (The Router):**  
    - Azure STT → `main.py` receives user text.
    - **$\text{AI}$ Intent Check:** Text $\rightarrow$ $\text{GPT-3.5}$ $\rightarrow$ Structured $\text{JSON}$ (`intent`, `slot`).
    - **Dispatch:** `main.py` executes the function (e.g., `feature_notes.run_notes_module("World History")`) based on the $\text{AI}$'s decision.
3. **Output:** Azure TTS plays audio response via speaker.  


---

##  Accessibility Impact  
- **Enhanced $\text{UX}$:** Intelligent natural language routing removes the complexity of menu hierarchies.
- **Stateful Interaction:** Persistent memory allows for seamless, personalized learning continuity.
- Fully usable without sight, keyboard, or requiring active internet connection for basic operation.  
- Builds **confidence** through mentorship and interactive learning.  
- Structured pacing improves comprehension.  
- Empowers **non-academic growth** via talk mode and personal notes.  

---

##  Future Scope  
- Full **Hybrid Offline Integration** using the $\text{Vosk/TinyLlama/Piper}$ modules. 
- Local language support (Hindi, Tamil, etc.).  
- Guardian dashboard for progress tracking.  
- Gamified quizzes and rewards.  
- Emotion-adaptive voice modulation.  
- Integration with Braille hardware.  

---

**AI²PBC** — *Transforming accessibility into real, inclusive education.*

