# AI²PBC  
**AI-powered Interactive Platform for Blind Children**  

##  Overview  
**AI²PBC** is an affordable, voice-first educational assistant designed to address the learning disadvantages faced by blind and low-vision students, especially in rural and under-resourced areas. Unlike basic screen readers, AI²PBC delivers **personalized learning, emotional engagement, and structured guidance**—all in an accessible, audio-only format.  

Built on a **Raspberry Pi** and powered by **Microsoft Azure Speech Services** and **OpenAI language models**, it works **offline-first** with optional cloud features for scalability. AI²PBC is portable, low-cost, and ideal for rural schools, low-income homes, and NGO deployments.  

---

##  Problem Statement  
Millions of blind and visually impaired children lack access to quality education due to:  
- Limited accessibility in existing tools.  
- No personalized or structured learning paths.  
- Lack of doubt-solving and emotional engagement.  
- High cost of commercial solutions.  

---

##  Objectives  
- Deliver a **low-cost, AI-powered tutor**.  
- Provide **structured audio-based lessons**.  
- Enable **real-time doubt-solving**.  
- Support **skill-building tests** and **personal notes**.  
- Operate **offline-first** with cloud scalability.  

---

##  Features  
- **Interactive Subject Learning** – Structured lessons with command control (`next`, `repeat`, `explain more`).  
- **AI-Powered Mentorship** – Real-time guidance and motivational support via GPT-3.5.  
- **Verbal Test Mode** – Chapter-wise tests (MCQs, fill-in-the-blanks, assertion-reason, short answers).  
- **Performance Reporting** – Auto-generated score reports emailed to guardians.  
- **Audio Notes Mode** – Record, organize, and replay spoken notes.  

---

##  Technology Stack  
**Hardware:**  
- Raspberry Pi 5  
- Microphone module  
- Bluetooth speaker  
- Waveshare UPS HAT (B)  

**Software:**  
- Python (modular scripts)  
- Azure Speech-to-Text & Text-to-Speech  
- OpenAI GPT-3.5-turbo  
- Local `.txt` lesson/test files  
- Gmail API for automated emails  

---

##  System Architecture  
1. **Input:** Voice commands via microphone.  
2. **Processing:**  
   - Azure STT → Command Router → Lesson/Test/Notes/GPT Query  
3. **Output:** Azure TTS plays audio via speaker.  


---

##  Accessibility Impact  
- Fully usable without sight, keyboard, or constant internet.  
- Builds **confidence** through mentorship and interactive learning.  
- Structured pacing improves comprehension.  
- Empowers **non-academic growth** via talk mode and personal notes.  

---

##  Future Scope  
- Local language support (Hindi, Tamil, etc.).  
- Guardian dashboard for progress tracking.  
- Gamified quizzes & rewards.  
- Emotion-adaptive voice modulation.  
- Integration with Braille hardware.  

---

**AI²PBC** — *Transforming accessibility into real, inclusive education.*  

