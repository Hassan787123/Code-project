import random
import pandas as pd
from collections import defaultdict

# ========== Employee Shift Allocator ==========
# Project Title: Employee Shift Allocator
# Author: Hassan Ali (F2022266069)
# Course: CS3045 - Artificial Intelligence
# ----------------------------------------------

# EMPLOYEE DATA
employees = [
    {
        "id": "E001",
        "name": "Alice Smith",
        "availability": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "preference": "Morning",
        "role": "Manager",
        "leave_days": ["Thu"],
        "seniority": 5
    },
    {
        "id": "E002",
        "name": "Bob Johnson",
        "availability": ["Tue", "Wed", "Thu", "Fri", "Sat"],
        "preference": "Evening",
        "role": "Clerk",
        "leave_days": [],
        "seniority": 3
    },
    {
        "id": "E003",
        "name": "Carol White",
        "availability": ["Mon", "Wed", "Fri"],
        "preference": "Day",
        "role": "Clerk",
        "leave_days": ["Fri"],
        "seniority": 2
    }
]

# CONFIG
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
shifts = ["Morning", "Evening", "Night"]
MAX_SHIFTS_PER_WEEK = 5
shift_requirements = {
    "Morning": 2,
    "Evening": 1,
    "Night": 1
}

# GLOBALS
conflict_log = []
assignment_log = []
shift_counts = defaultdict(lambda: defaultdict(int))  # shift_counts[day][shift]
assigned_shifts = defaultdict(int)
previous_shift = defaultdict(lambda: None)
penalty_score = defaultdict(int)


# VALIDATION: Ensures employee data integrity
def validate_employee_data():
    print("Validating employee data...")
    for emp in employees:
        for key in ["id", "name", "availability", "preference", "role", "leave_days", "seniority"]:
            if key not in emp:
                print(f"⚠️ Missing {key} for employee: {emp.get('name', 'UNKNOWN')}")
    print("Validation complete.\n")


# AI DECISION LOGIC: Assign one shift per day
def assign_shift(emp, day):
    emp_id = emp["id"]
    if day not in emp["availability"] or day in emp["leave_days"]:
        return "OFF"

    # Rule: No consecutive night shifts
    options = [s for s in shifts if not (previous_shift[emp_id] == "Night" and s == "Night")]

    # Preference boost
    if emp["preference"] in options and random.random() < 0.7:
        shift = emp["preference"]
    else:
        shift = random.choice(options)

    # Enforce staffing limits
    if shift_counts[day][shift] >= shift_requirements[shift]:
        assignment_log.append(f"{emp['name']} skipped on {day} — shift full")
        return "OFF"

    # Max shifts limit
    if assigned_shifts[emp_id] >= MAX_SHIFTS_PER_WEEK:
        assignment_log.append(f"{emp['name']} skipped on {day} — max shifts reached")
        return "OFF"

    # Apply assignment
    assigned_shifts[emp_id] += 1
    shift_counts[day][shift] += 1
    previous_shift[emp_id] = shift
    assignment_log.append(f"{emp['name']} assigned {shift} on {day}")

    # Penalty system
    if shift != emp["preference"]:
        penalty_score[emp_id] += 1
    if day in emp["leave_days"]:
        penalty_score[emp_id] += 5
        conflict_log.append(f"{emp['name']} assigned on leave day {day}.")

    return shift


# BUILD SCHEDULE
def generate_schedule():
    schedule = []
    for emp in employees:
        row = {"EmployeeID": emp["id"], "Name": emp["name"], "Role": emp["role"]}
        for day in days:
            shift = assign_shift(emp, day)
            row[day] = shift
        schedule.append(row)
    return pd.DataFrame(schedule)

# SCHEDULE EVALUATION
def evaluate_schedule(df):
    print("\n=== AI Evaluation Metrics ===")
    for emp in employees:
        emp_id = emp["id"]
        total_shifts = assigned_shifts[emp_id]
        penalties = penalty_score[emp_id]
        print(f"{emp['name']} → Shifts: {total_shifts}, Penalty: {penalties}")

    fairness_gap = max(assigned_shifts.values()) - min(assigned_shifts.values())
    print(f"\n📊 Fairness Gap (ideal = 0): {fairness_gap}")
    print("✅ Schedule generated with AI balance.\n")


# SHOW VISUAL VIEW
def display_schedule(df):
    print("📅 Final Weekly Shift Table:")
    print(df.to_string(index=False))


# WEEKLY REPORT
def weekly_summary(df):
    print("\n=== Weekly Summary Report ===")
    for emp in employees:
        row = df[df["EmployeeID"] == emp["id"]].iloc[0]
        total = sum(1 for day in days if row[day] != "OFF")
        preferred = sum(1 for day in days if row[day] == emp["preference"])
        print(f"{emp['name']} → Total: {total} | Preferred Match: {preferred}")


# SAVE TO FILE
def save_schedule(df):
    df.to_csv("Final_Shift_Schedule.csv", index=False)
    with open("Assignment_Log.txt", "w") as f:
        for line in assignment_log:
            f.write(line + "\n")
    print("\n📝 Saved schedule to CSV and log file.")


# MAIN FUNCTION
def main():
    print("🚀 Running Employee Shift Allocator...\n")
    validate_employee_data()
    schedule = generate_schedule()
    display_schedule(schedule)
    evaluate_schedule(schedule)
    weekly_summary(schedule)
    save_schedule(schedule)

    if conflict_log:
        print("\n⚠️ Conflicts:")
        for c in conflict_log:
            print(" -", c)
    else:
        print("\n✅ No major conflicts detected.")

# Run
if __name__ == "__main__":
    main()
