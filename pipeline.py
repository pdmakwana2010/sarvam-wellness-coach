import os
import json
import re
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

# Ensure .env is loaded
env_file = Path(__file__).resolve().parent / ".env"
if env_file.is_file():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

from sarvamai import SarvamAI


# --- Structured Pydantic Schemas ---

class MealItem(BaseModel):
    item_name: str = Field(description="Name of the food item or dish")
    portion: str = Field(description="Estimated portion size or quantity")
    calories: float = Field(description="Estimated calories in kcal")
    protein_g: float = Field(description="Estimated protein in grams")
    carbs_g: float = Field(description="Estimated carbohydrates in grams")
    fat_g: float = Field(description="Estimated fats in grams")
    meal_type: str = Field(description="Breakfast, Lunch, Dinner, or Snack")


class WorkoutItem(BaseModel):
    activity: str = Field(description="Type of workout or physical activity")
    duration_minutes: float = Field(description="Duration in minutes")
    intensity: str = Field(description="Low, Moderate, or High")
    calories_burned: float = Field(description="Estimated calories burned")


class SleepRecovery(BaseModel):
    hours_slept: float = Field(description="Hours of sleep reported")
    quality: str = Field(description="Good, Fair, or Poor")
    energy_level: str = Field(description="High, Moderate, Low, or Exhausted")
    notes: str = Field(description="Observations on fatigue or sleep debt")


class DailyTotals(BaseModel):
    total_calories_in: float = Field(description="Total caloric intake")
    total_calories_burned: float = Field(description="Total calories burned through exercise")
    net_calories: float = Field(description="Caloric intake minus workout burn")
    total_protein_g: float = Field(description="Total protein in grams")
    total_carbs_g: float = Field(description="Total carbohydrates in grams")
    total_fat_g: float = Field(description="Total fats in grams")


class CoachFeedback(BaseModel):
    acknowledgement: str = Field(description="Warm, empathetic check-in acknowledgment")
    nutrition_feedback: str = Field(description="Evaluation of macros and nutrition balance")
    workout_feedback: str = Field(description="Feedback on workout consistency and effort")
    adaptive_adjustment: str = Field(description="Plan adjustment based on energy, sleep, or missed workouts")
    spoken_nudge: str = Field(description="Short natural spoken response suitable for TTS (in conversational Hinglish/English)")


class WellnessCheckInResult(BaseModel):
    meals: List[MealItem] = Field(default_factory=list)
    workouts: List[WorkoutItem] = Field(default_factory=list)
    sleep_and_recovery: SleepRecovery
    daily_totals: DailyTotals
    coach_feedback: CoachFeedback


# --- Extractor Engine ---

class WellnessCoachExtractor:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.environ.get("SARVAM_API_KEY")
        if not key:
            raise ValueError("SARVAM_API_KEY must be set in environment or passed to constructor.")
        self.client = SarvamAI(api_subscription_key=key)
        self.model = "sarvam-105b-conversations"

    def _get_system_prompt(self) -> str:
        return """You are the AI Intelligence Engine for an Indic Wellness & Health Coach.
Your task is to analyze natural language or voice transcripts from daily user health check-ins.
The input is frequently spoken in code-mixed Indian languages (e.g. Hinglish, Tanglish, English mixed with Hindi, etc.).

Analyze the input thoroughly:
1. Food & Nutrition:
   - Identify traditional Indian foods (e.g. roti, paratha, dal, sabzi, idli, dosa, curd/dahi, biryani, poha, upma, paneer dishes, chai).
   - Accurately estimate portion sizes and reasonable macro nutrients (calories, protein, carbs, fat).
   - Classify meal type (Breakfast, Lunch, Dinner, Snack).

2. Workouts & Activity:
   - Extract exercises (gym, walking, running, yoga, sport, home workout).
   - Extract duration and estimate calories burned based on intensity.

3. Sleep & Energy:
   - Extract sleep duration and reported energy/fatigue levels.

4. Daily Totals:
   - Calculate total calories in, calories burned, net calories, and total macros.

5. Adaptive Coaching:
   - If user had low sleep (< 6 hours) or feels tired, adapt tomorrow's plan towards recovery, hydration, and light activity instead of high-strain training.
   - If workout was missed, provide an encouraging nudge without guilt and suggest a quick 10-15 min alternative.
   - Provide a 'spoken_nudge' that sounds natural, warm, and friendly when spoken aloud by an Indian voice AI (conversational blend of English and common friendly Indic phrasing).

You MUST respond strictly with a valid JSON object matching this exact schema:
{
  "meals": [
    {
      "item_name": "...",
      "portion": "...",
      "calories": 0.0,
      "protein_g": 0.0,
      "carbs_g": 0.0,
      "fat_g": 0.0,
      "meal_type": "Breakfast"
    }
  ],
  "workouts": [
    {
      "activity": "...",
      "duration_minutes": 0.0,
      "intensity": "Moderate",
      "calories_burned": 0.0
    }
  ],
  "sleep_and_recovery": {
    "hours_slept": 0.0,
    "quality": "Good",
    "energy_level": "Moderate",
    "notes": "..."
  },
  "daily_totals": {
    "total_calories_in": 0.0,
    "total_calories_burned": 0.0,
    "net_calories": 0.0,
    "total_protein_g": 0.0,
    "total_carbs_g": 0.0,
    "total_fat_g": 0.0
  },
  "coach_feedback": {
    "acknowledgement": "...",
    "nutrition_feedback": "...",
    "workout_feedback": "...",
    "adaptive_adjustment": "...",
    "spoken_nudge": "..."
  }
}
"""

    def extract(self, transcript: str) -> WellnessCheckInResult:
        """Processes user check-in transcript and returns validated WellnessCheckInResult."""
        response = self.client.chat.completions(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"User Check-in Transcript:\n\"\"\"{transcript}\"\"\""}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()

        # Handle possible markdown backticks
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
            content = re.sub(r"\n?```$", "", content).strip()

        data = json.loads(content)
        return WellnessCheckInResult(**data)
