from datetime import time, timedelta

WORK_DAYS = {"Mon", "Tue", "Thu", "Fri"}
MEALS_PER_PREP = 3  # 3 lunches and 3 dinners per meal prep

available_lunches = MEALS_PER_PREP
available_dinners = MEALS_PER_PREP

def merge_blocks(blocks):
    blocks = sorted(blocks, key=lambda x: x[0])
    merged = []
    for start, end, task in blocks:
        if not merged:
            merged.append([start, end, task])
        else:
            last = merged[-1]
            if last[1] >= start and last[2] == task:
                last[1] = max(last[1], end)
            else:
                merged.append([start, end, task])
    return [(s, e, t) for s, e, t in merged]

def add_minutes(t, mins):
    full_minutes = t.hour*60 + t.minute + mins
    hour = full_minutes // 60
    minute = full_minutes % 60
    if hour >= 24:
        hour -= 24
    return time(hour, minute)

def make_schedule(day: str, lectures: list, uni_done=False):
    global available_lunches, available_dinners
    schedule = []

    # Morning routine
    schedule.append((time(7,30), time(7,45), "Wake up & morning routine"))
    schedule.append((time(7,45), time(8,0), "Breakfast"))

    # Shopping/meal prep days
    last_end = time(8,0)
    if day in {"Sun", "Wed"}:
        schedule.append((time(8,0), time(10,0), "Shopping & meal prep"))
        available_lunches = MEALS_PER_PREP
        available_dinners = MEALS_PER_PREP
        last_end = time(10,0)
        if lectures and lectures[0][0] > last_end:
            schedule.append((last_end, lectures[0][0], "Relax"))
            last_end = lectures[0][0]

    # Insert lectures
    for start, end in lectures:
        schedule.append((start, end, "Lecture"))

    # Insert lunch around 12:30 if possible
    lunch_added = False
    for start, end in lectures:
        gap_start = last_end
        gap_end = start
        gap_minutes = (gap_end.hour*60 + gap_end.minute) - (gap_start.hour*60 + gap_start.minute)

        if not lunch_added and available_lunches > 0:
            lunch_start = time(12,30)
            if gap_start <= lunch_start < gap_end:
                if (lunch_start.hour*60 + lunch_start.minute - gap_start.hour*60 - gap_start.minute) >= 15:
                    schedule.append((gap_start, lunch_start, "Math study" if uni_done else "Uni work"))
                lunch_end = add_minutes(lunch_start, 30)
                schedule.append((lunch_start, lunch_end, "Lunch"))
                available_lunches -= 1
                last_end = lunch_end
                lunch_added = True
                continue

        if gap_minutes >= 60:
            schedule.append((gap_start, gap_end, "Math study" if uni_done else "Uni work"))
        last_end = max(last_end, end)

    # Ensure lunch if not yet eaten today
    if not lunch_added and available_lunches > 0:
        lunch_start = max(last_end, time(12,30))
        lunch_end = add_minutes(lunch_start, 30)
        schedule.append((lunch_start, lunch_end, "Lunch"))
        available_lunches -= 1
        last_end = lunch_end

    # Fill remaining day
    if day in WORK_DAYS:
        if last_end < time(16,30):
            schedule.append((last_end, time(16,30), "Math study" if uni_done else "Uni work"))
        schedule.append((time(16,30), time(16,40), "Prepare for work + snack"))
        schedule.append((time(16,40), time(21,20), "Work (incl. commute)"))
        schedule.append((time(21,20), time(21,30), "Shower after work"))
        if available_dinners > 0:
            schedule.append((time(21,30), time(22,0), "Dinner"))
            available_dinners -= 1
        schedule.append((time(22,0), time(22,5), "Make breakfast for tomorrow"))
        schedule.append((time(22,5), time(22,15), "Bedtime routine"))
        schedule.append((time(22,15), time(0,0), "Free time"))
    else:
        # Non-workdays: continue Math study until evening with snack at 16:00
        if last_end < time(16,0):
            schedule.append((last_end, time(16,0), "Math study" if uni_done else "Uni work"))
            last_end = time(16,0)
        schedule.append((time(16,0), time(16,15), "Snack"))
        last_end = time(16,15)
        if last_end < time(20,0):
            schedule.append((last_end, time(20,0), "Math study" if uni_done else "Uni work"))
            last_end = time(20,0)
        schedule.append((time(20,0), time(20,10), "Shower"))
        schedule.append((time(20,10), time(21,0), "Relax"))
        if available_dinners > 0:
            schedule.append((time(21,0), time(21,30), "Dinner"))
            available_dinners -= 1
        schedule.append((time(21,30), time(21,35), "Make breakfast for tomorrow"))
        schedule.append((time(21,35), time(21,45), "Bedtime routine"))
        schedule.append((time(21,45), time(0,0), "Free time"))

    schedule = merge_blocks(schedule)
    return sorted(schedule, key=lambda x: x[0])

# Prompt user for input
day = input("Enter day (Mon, Tue, Wed, Thu, Fri, Sat, Sun): ").strip()
lectures = []
while True:
    add = input("Add a lecture? (y/n): ").strip().lower()
    if add != 'y':
        break
    start_str = input("Start time (HH:MM): ").strip()
    end_str = input("End time (HH:MM): ").strip()
    start_h, start_m = map(int, start_str.split(':'))
    end_h, end_m = map(int, end_str.split(':'))
    lectures.append((time(start_h, start_m), time(end_h, end_m)))

uni_done = input("All uni work done already? (y/n): ").strip().lower() == 'y'

schedule = make_schedule(day, lectures, uni_done)

print("\nSchedule:")
for start, end, task in schedule:
    print(f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')} : {task}")

print(f"\nAvailable lunches left: {available_lunches}")
print(f"Available dinners left: {available_dinners}")

