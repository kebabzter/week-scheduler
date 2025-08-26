from datetime import time, timedelta

WORK_DAYS = {"Mon", "Tue", "Thu", "Fri"}

# ANSI color codes for terminal output
COLOR_RESET = '\033[0m'
COLOR_BOLD = '\033[1m'
COLOR_MORNING = '\033[95m'
COLOR_LECTURE = '\033[94m'
COLOR_STUDY = '\033[92m'
COLOR_MEAL = '\033[93m'
COLOR_WORK = '\033[91m'
COLOR_RELAX = '\033[96m'


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


def color_task(task):
    if 'Lecture' in task:
        return COLOR_LECTURE
    elif 'Math' in task or 'Uni' in task:
        return COLOR_STUDY
    elif 'Breakfast' in task or 'Snack' in task:
        return COLOR_MEAL
    elif 'Work' in task or 'Prepare for work' in task:
        return COLOR_WORK
    elif 'Relax' in task or 'Wait' in task:
        return COLOR_RELAX
    else:
        return COLOR_MORNING


def make_schedule(day: str, lectures: list, uni_done=False):
    schedule = []

    # Morning routine
    schedule.append((time(7,30), time(7,45), "Wake up & morning routine"))
    schedule.append((time(7,45), time(8,0), "Breakfast"))

    # Shopping/meal prep days
    last_end = time(8,0)
    if day in {"Sun", "Wed"}:
        schedule.append((time(8,0), time(10,0), "Shopping & meal prep"))
        last_end = time(10,0)
        if lectures and lectures[0][0] > last_end:
            schedule.append((last_end, lectures[0][0], "Relax"))
            last_end = lectures[0][0]

    # Insert lectures and study blocks
    for start, end in lectures:
        gap_start = last_end
        gap_end = start
        gap_minutes = (gap_end.hour*60 + gap_end.minute) - (gap_start.hour*60 + gap_start.minute)
        if gap_minutes >= 60:
            schedule.append((gap_start, gap_end, "Math study" if uni_done else "Uni work"))
        schedule.append((start, end, "Lecture"))
        last_end = end

    # Fill remaining day
    day_end_time = time(16,30) if day in WORK_DAYS else time(20,0)
    if last_end < day_end_time:
        schedule.append((last_end, day_end_time, "Math study" if uni_done else "Uni work"))
        last_end = day_end_time

    if day in WORK_DAYS:
        schedule.append((time(16,30), time(16,40), "Prepare for work + snack"))
        schedule.append((time(16,40), time(21,20), "Work (incl. commute)"))
        schedule.append((time(21,20), time(21,30), "Shower after work"))
        schedule.append((time(21,30), time(22,0), "Dinner"))
        schedule.append((time(22,0), time(22,5), "Make breakfast for tomorrow"))
        schedule.append((time(22,5), time(22,15), "Bedtime routine"))
        schedule.append((time(22,15), time(0,0), "Free time"))
    else:
        schedule.append((time(16,0), time(16,15), "Snack"))
        if last_end < time(20,0):
            schedule.append((time(16,15), time(20,0), "Math study" if uni_done else "Uni work"))
        schedule.append((time(20,0), time(20,10), "Shower"))
        schedule.append((time(20,10), time(21,0), "Relax"))
        schedule.append((time(21,0), time(21,30), "Dinner"))
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

print(f"\n{COLOR_BOLD}Schedule for {day}:{COLOR_RESET}")
for start, end, task in schedule:
    color = color_task(task)
    print(f"{color}{start.strftime('%H:%M')} - {end.strftime('%H:%M')} : {task}{COLOR_RESET}")

