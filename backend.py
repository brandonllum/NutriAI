from google import genai
import glob
import numpy as np
from datascience import *
import re
import pandas as pd
from helper_functions import *
import json
from datetime import datetime, timedelta




def save_to_weekly(day_name, meal_plan, water_schedule, calorie_intake, macros):
    """Save the current plan to the weekly schedule"""
    weekly_schedule[day_name] = {
        "meal_plan": meal_plan,
        "water_schedule": water_schedule.tolist() if isinstance(water_schedule, np.ndarray) else water_schedule,
        "calorie_intake": calorie_intake,
        "macros": macros
    }
    
    # Save to file
    with open("weekly_schedule.json", "w") as f:
        json.dump(weekly_schedule, f, indent=2)

def load_weekly_schedule():
    """Load existing weekly schedule from file"""
    try:
        with open("weekly_schedule.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

weekly_schedule = make_array()
weekly_schedule = load_weekly_schedule()
profile = make_array();


client = genai.Client(api_key="YOUR_API_KEY")

txt_folder = "txts/"
txt_files = glob.glob(txt_folder + "*.txt")
combined_context = "".join(f"\n---\nContent from {txt}:\n{extract_text_from_txt(txt)}" for txt in txt_files)

profile = get_user_profile()

while True:
    try:
        exercise_minutes = float(input("Enter how many minutes you exercise each day: "))
        if exercise_minutes < 0:
            raise ValueError
        break
    except ValueError:
        print("Please enter a valid number for exercise minutes.")

water_schedule = get_water_schedule(get_water_sum(profile["weight"], exercise_minutes))
activity_multiplier = get_activity_multiplier()
calorie_intake = get_hb_BMR(profile, activity_multiplier)
calorie_intake, goal = adjust_for_goal(calorie_intake)
macros = get_macros(calorie_intake)

print(f"\n🎯 Based on your goal to *{goal}*, here’s your adjusted intake:")
print("✅ Your Recommended Daily Calorie Intake:", calorie_intake)
print("✅ Your Recommended Daily Macronutrient Intake:")
for key, value in macros.items():
    print(f"{key}: {value}")
print("\n✅ Your Recommended Water Intake Schedule:")
print(water_schedule)

food_data = pd.read_csv("full_branded_food_macros.csv", low_memory=False)
food_data = food_data[["food_name", "Protein (g)", "Carbs (g)", "Fat (g)"]].dropna()
food_data.columns = ["Description", "Protein (g)", "Carbohydrates (g)", "Fats (g)"]
food_data["Calories"] = (
    food_data["Protein (g)"] * 4 +
    food_data["Carbohydrates (g)"] * 4 +
    food_data["Fats (g)"] * 9
).round(0)

sampled_food_data = food_data.sample(n=100, random_state=42)
food_list = "".join(
    f"{row['Description']}: {row['Protein (g)']}g protein, {row['Carbohydrates (g)']}g carbs, "
    f"{row['Fats (g)']}g fats, {row['Calories']} kcal\n"
    for _, row in sampled_food_data.iterrows()
)

initial_meal_prompt = (
    f"Based on the following daily macronutrient goals:\n"
    f"Calories: {calorie_intake}\n"
    f"Protein (g): {macros['Protein (g)']}\n"
    f"Carbohydrates (g): {macros['Carbohydrates (g)']}\n"
    f"Fats (g): {macros['Fats (g)']}\n"
    f"Create a full day's meal plan (breakfast, lunch, dinner, snacks) that matches these targets.\n"
    f"Use these foods:\n{food_list}\n\n"
    f"Respond in **this exact format below**. Do not use JSON or markdown. Do not include any explanations, introductions notes, or additional texts like proposed adjustments, or alternative food choices, nor **Notes** or *Okay, here is a meal plan designed to meet your macronutrient goals, using only the provided food items. Please note that due to the limitations of the food list, achieving the exact target values is very difficult. This is an approximation.*.\n"
    "Meal Plan:\n"
    "Breakfast:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n"
    "Lunch:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n"
    "Dinner:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n"
    "Snacks:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n\n"
    "Total Macros:\n"
    "Protein: Xg\nCarbs: Yg\nFats: Zg\nCalories: N kcal"
)

initial_meal_response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=initial_meal_prompt
)

print("\n🍽️ Gemini's Initial Suggested Meal Plan:")
print(initial_meal_response.text)

if input("\nWould you like to make adjustments? (Yes/No): ").strip().upper() == "YES":
    customization = True
else:
    customization = False

while customization:
    custom_changes = input("\nDescribe adjustments (e.g., 'increase protein', 'make vegetarian'): ")

    full_prompt = (
        f"Current calorie intake: {calorie_intake}\n"
        f"Current macros: Protein {macros['Protein (g)']}g, Carbs {macros['Carbohydrates (g)']}g, Fats {macros['Fats (g)']}g\n"
        f"Current water schedule: {str(water_schedule)}\n\n"
        f"User request: {custom_changes}\n\n"
        f"Here are some available foods:\n{food_list}\n\n"
        "Respond in **this exact format below**. Do not use JSON or markdown. Do not include any explanations, introductions notes, or additional texts like proposed adjustments, or alternative food choices, nor **Notes** or *Okay, here is a meal plan designed to meet your macronutrient goals, using only the provided food items. Please note that due to the limitations of the food list, achieving the exact target values is very difficult. This is an approximation.*.\n"
        "Strictly follow this structure and return only this:\n\n"
        "Calories: [number]\n"
        "Protein (g): [number]\n"
        "Carbohydrates (g): [number]\n"
        "Fats (g): [number]\n\n"
        "Water:\n"
        "HH:MM - XXml\n"
        "...\n\n"
        "Meal Plan:\n"
        "Breakfast:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n"
        "Lunch:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n"
        "Dinner:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n"
        "Snacks:\n- [Food] - Xg protein, Yg carbs, Zg fat, N kcal\n\n"
        "Total Macros:\n"
        "Protein: Xg\nCarbs: Yg\nFats: Zg\nCalories: N kcal"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )

        updated_text = response.text
        calorie_intake, macros = parse_updated_values(updated_text, calorie_intake, macros)
        water_schedule = parse_updated_water_schedule(updated_text, water_schedule)

        print("\n✅ Updated Water Intake Schedule:")
        print(water_schedule)
        print("\n✅ Updated Calorie Intake:", calorie_intake)
        print("✅ Updated Macronutrient Breakdown:")
        for key, value in macros.items():
            print(f"{key}: {value}")

        print("\n🍽️ Gemini's Updated Meal Plan:")
        print(updated_text)

    except Exception as e:
        print("⚠️ Error generating updated meal plan:", str(e))

    if input("\nWould you like to make further adjustments? (Yes/No): ").strip().upper() != "YES":
        customization = False

current_day = datetime.now().strftime("%A")  # Or let user choose
save_option = input(f"\nWould you like to save this plan for {current_day}? (Yes/No): ").strip().upper()
if save_option == "YES":
    save_to_weekly(
        current_day,
        initial_meal_response.text if not customization else updated_text,
        water_schedule,
        calorie_intake,
        macros
    )
    print(f"✅ Plan saved for {current_day}!")

# Add meal plan to weekly schedule
if input("\nWould you like to view your weekly schedule? (Yes/No): ").strip().upper() == "YES":
    print("\n📅 Weekly Schedule:")
    for day, plan in weekly_schedule.items():
        print(f"\n--- {day} ---")
        print("Water Schedule:")
        if isinstance(plan["water_schedule"], list):
            for i in range(0, len(plan["water_schedule"]), 2):
                print(f"{plan['water_schedule'][i]}: {plan['water_schedule'][i+1]}")
        else:
            print(plan["water_schedule"])
        print(f"\nCalories: {plan['calorie_intake']}")
        print("Macros:", plan["macros"])
        print("\nMeal Plan:")
        print(plan["meal_plan"])
