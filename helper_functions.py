import numpy as np
from datascience import *
import re

# --- Helper functions ---
#    
def parse_updated_values(text, calorie_intake, macros):
    calorie_match = re.search(r'(?i)calories?:?\s*(\d+)', text)
    if calorie_match:
        calorie_intake = int(calorie_match.group(1))

    protein_match = re.search(r'(?i)protein\s*\(?.*g\)?:?\s*(\d+)', text)
    carbs_match = re.search(r'(?i)carb(?:s|ohydrates)?\s*\(?.*g\)?:?\s*(\d+)', text)
    fats_match = re.search(r'(?i)fat(?:s)?\s*\(?.*g\)?:?\s*(\d+)', text)

    if protein_match:
        macros["Protein (g)"] = int(protein_match.group(1))
    if carbs_match:
        macros["Carbohydrates (g)"] = int(carbs_match.group(1))
    if fats_match:
        macros["Fats (g)"] = int(fats_match.group(1))

    return calorie_intake, macros

def parse_updated_water_schedule(text, water_schedule):
    matches = re.findall(r'(\d{1,2}:\d{2})\s*[-:]\s*(\d+)\s*ml', text, re.IGNORECASE)
    if matches:
        updated_schedule = make_array()
        for time, amount in matches:
            updated_schedule = np.append(updated_schedule, time)
            updated_schedule = np.append(updated_schedule, f"{amount}ml")
        return updated_schedule
    else:
        return water_schedule

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_water_sum(bodyweight, exercise_minutes):
    water_oz = (bodyweight / 2) + ((exercise_minutes / 30) * 12)
    return water_oz * 29.5735

def get_water_schedule(water_sum):
    while True:
        try:
            wakeup_hour = int(input("What time do you usually wake up? (24-hour format): "))
            if not 0 <= wakeup_hour <= 23:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a valid hour (0–23).")

    while True:
        try:
            bedtime_hour = int(input("What time do you usually sleep? (24-hour format): "))
            if not 0 <= bedtime_hour <= 23 or bedtime_hour <= wakeup_hour:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a valid hour later than wake-up time (0–23).")

    water_schedule = make_array()
    avg_water = water_sum / (bedtime_hour - wakeup_hour)

    for i in np.arange(wakeup_hour, bedtime_hour):
        water_schedule = np.append(water_schedule, f"{i}:00")
        water_schedule = np.append(water_schedule, f"{np.round(avg_water)}ml")

    return water_schedule

def get_activity_multiplier():
    print("\nChoose your activity level:")
    print("1. Sedentary (little or no exercise)")
    print("2. Lightly active (light exercise/sports 1-3 days/week)")
    print("3. Moderately active (moderate exercise/sports 3-5 days/week)")
    print("4. Very active (hard exercise/sports 6-7 days a week)")
    print("5. Extra active (very hard exercise + physical job or 2x training)")

    while True:
        try:
            level = int(input("Enter the number corresponding to your activity level (1-5): "))
            if level not in range(1, 6):
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please choose a number from 1 to 5.")

    return {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}[level]

def get_user_profile():
    print("\n--- User Profile Setup ---")
    gender_input = input("Enter your gender: ").strip().lower()
    if gender_input == "male" :
        gender = "male" 

    while True:
        try:
            weight = float(input("Enter your bodyweight (lb): "))
            if weight <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number for weight.")

    while True:
        try:
            height = int(input("Enter height in cm: "))
            if height <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number for height.")

    while True:
        try:
            age = int(input("Enter age in years: "))
            if age <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number for age.")

    return {"gender": gender, "weight": weight, "height": height, "age": age}

def get_hb_BMR(profile, activity_multiplier):
    gender = profile["gender"]
    weight_kg = profile["weight"] * 0.453592
    height = profile["height"]
    age = profile["age"]

    if gender == "male":
        bmr = 66.5 + (13.75 * weight_kg) + (5.003 * height) - (6.75 * age)
    else:
        bmr = 655.1 + (9.563 * weight_kg) + (1.850 * height) - (4.676 * age)

    return int(np.round(bmr * activity_multiplier))

def adjust_for_goal(calorie_intake):
    print("\nWhat's your current fitness goal?")
    print("1. Bulk (gain muscle)")
    print("2. Cut (lose fat)")
    print("3. Maintain")

    while True:
        try:
            goal_choice = int(input("Enter 1, 2, or 3: "))
            if goal_choice not in [1, 2, 3]:
                raise ValueError
            break
        except ValueError:
            print("Invalid choice. Please enter 1, 2, or 3.")

    if goal_choice == 1:
        print("⚡ Goal: Bulk – increasing calories by 15%")
        return int(calorie_intake * 1.15), "bulk"
    elif goal_choice == 2:
        print("🔥 Goal: Cut – reducing calories by 20%")
        return int(calorie_intake * 0.80), "cut"
    else:
        print("🎯 Goal: Maintain – keeping calorie intake unchanged")
        return calorie_intake, "maintain"

def get_macros(calorie_intake):
    protein = (calorie_intake * 0.30) / 4
    carbs = (calorie_intake * 0.45) / 4
    fats = (calorie_intake * 0.25) / 9
    return {
        "Protein (g)": round(protein),
        "Carbohydrates (g)": round(carbs),
        "Fats (g)": round(fats)
    }

# --- Setup ---