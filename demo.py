import sys
from pipeline import WellnessCoachExtractor


def run_pipeline(text: str):
    extractor = WellnessCoachExtractor()
    print("=" * 70)
    print("      SARVAM AI - INDIC WELLNESS COACH EXTRACTION PIPELINE")
    print("=" * 70)
    print(f"\nUser Spoken Check-in:\n\"{text}\"\n")
    print("Processing with sarvam-105b-conversations...\n")

    result = extractor.extract(text)

    print("--- Extracted Meals & Macros ---")
    if result.meals:
        for m in result.meals:
            print(f"  • [{m.meal_type}] {m.item_name} ({m.portion}) -> {m.calories:.0f} kcal "
                  f"| Protein: {m.protein_g:.1f}g, Carbs: {m.carbs_g:.1f}g, Fat: {m.fat_g:.1f}g")
    else:
        print("  • No meals reported in this check-in.")

    print("\n--- Extracted Workouts ---")
    if result.workouts:
        for w in result.workouts:
            print(f"  • {w.activity}: {w.duration_minutes:.0f} mins ({w.intensity} intensity) "
                  f"-> ~{w.calories_burned:.0f} kcal burned")
    else:
        print("  • No workouts completed.")

    print("\n--- Sleep & Recovery ---")
    sr = result.sleep_and_recovery
    print(f"  • Sleep: {sr.hours_slept} hrs ({sr.quality}) | Energy: {sr.energy_level}")
    print(f"  • Notes: {sr.notes}")

    print("\n--- Daily Totals ---")
    dt = result.daily_totals
    print(f"  • Calories: {dt.total_calories_in:.0f} in - {dt.total_calories_burned:.0f} burned = {dt.net_calories:.0f} net")
    print(f"  • Macros: Protein: {dt.total_protein_g:.1f}g | Carbs: {dt.total_carbs_g:.1f}g | Fat: {dt.total_fat_g:.1f}g")

    print("\n--- Adaptive Coaching Feedback ---")
    fb = result.coach_feedback
    print(f"  • Acknowledgment: {fb.acknowledgement}")
    print(f"  • Nutrition: {fb.nutrition_feedback}")
    print(f"  • Workout: {fb.workout_feedback}")
    print(f"  • Adaptive Plan: {fb.adaptive_adjustment}")
    print(f"\n[Spoken Nudge (TTS ready)]: \"{fb.spoken_nudge}\"")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_input = " ".join(sys.argv[1:])
        run_pipeline(custom_input)
    else:
        # Default realistic check-in
        default_checkin = (
            "Subah 2 methi parathe dahi ke sath khaye. Lunch me rajma chawal with cucumber salad. "
            "Sham ko 45 min dumbbell workout aur 15 min cardio kiya gym me. "
            "Par neend kal raat sirf 5 ghante hui, thoda tired feel ho raha hai."
        )
        run_pipeline(default_checkin)
