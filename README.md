# Sarvam Indic Wellness Coach

An AI-powered voice and health intelligence application designed for Indian users. It automates daily health tracking by analyzing natural, code-mixed Indian language check-ins (food intake, workouts, and sleep) and provides personalized adaptive health coaching with voice feedback.

Powered by **[Sarvam AI](https://sarvam.ai/)**:
- **`sarvam-105b-conversations`**: Extracts Indian cuisine nutrition (macros, calories), workout metrics, and sleep fatigue indicators into structured JSON.
- **`bulbul:v3`**: Synthesizes the coach's personalized feedback into natural Indian spoken voice (TTS).

---

## Features

- **Indic Food & Nutrition Intelligence**: Accurately recognizes traditional Indian meals (parathas, rajma chawal, idli-sambar, curd rice, paneer bhurji, etc.) and calculates calories, protein, carbs, and fat.
- **Workout & Active Burn Tracking**: Estimates calorie expenditure for workouts, gym sessions, yoga, and walking.
- **Sleep & Fatigue Adaptation**: Detects sleep deficit and automatically dials down training intensity recommendations for active recovery.
- **Browser Voice Input**: Speak directly using the microphone button with speech recognition support.
- **Voice Feedback Audio Player**: Listen to your coach's voice note directly in the browser with selectable Indian voice personas (Ishita, Simran, Rahul, Aditya).
- **Quick-Start Presets**: 1-click test buttons with realistic Hinglish and regional Indian check-in scenarios.

---

## Project Structure

```
sarvam_project/
├── app.py             # FastAPI backend with REST endpoints & Bulbul TTS
├── pipeline.py        # Core extraction pipeline using sarvam-105b-conversations
├── demo.py            # CLI test runner for terminal check-ins
├── main.py            # Minimal API test script
├── static/
│   └── index.html     # Modern responsive single-page frontend (Tailwind CSS)
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
└── .gitignore         # Ignores .env and cache
```

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/sarvam-wellness-coach.git
cd sarvam-wellness-coach
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```
*(Get your key from [Sarvam AI Indus Dashboard](https://indus.sarvam.ai/))*

---

## Running the Application

### Web Application
Start the FastAPI server:
```bash
python -m uvicorn app:app --port 8000 --host 127.0.0.1
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### Command-Line Demo
Run terminal check-ins:
```bash
# Default check-in
python demo.py

# Custom check-in
python demo.py "Breakfast me 3 idli with sambar khaya. 30 min evening walk ki. 7 hrs neend hui."
```

---

## License
MIT
