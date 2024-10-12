import utils
from schedule_builder_funcs import *
from datetime import datetime
course_input = ""
all_course_data = utils.read_data_from_json("data/course_data_202501.json")

i = 1
sections = []
courses = []
credits = 0
pace = 0
earliest_start = 0
latest_end = 0

print("Enter course or section id (i.e. CMSC351, ENGL101-0001), or \"done\" when finished")
while True:
    course_input = input(f"{i}) ").upper()
    if course_input == "DONE":
        break
    try:
        read = read_course(course_input, all_course_data)
        credits += read.credits
        if credits > 20:
            print("> 20 credits entered, try again or type \"done\"")
            continue
        if type(read) == Course:
            courses.append(read)
        else:
            if overlaps_schedule(read, sections, LITERALLY_TELEPORTING_PACE):
                print(f"{course_input} overlaps with schedule, try again")
                continue
            sections.append(read)
        i += 1
    except Exception as e:
        print(f"{e}, try again")
print("Enter your movement pace (normal/fast/jogging/biking/scooter)")
while True:
    dic = {"normal": NORMAL_WALKING_PACE, "fast": FAST_WALKING_PACE, "jogging": JOGGING_PACE, "biking": BIKING_SCOOTER_PACE, "scooter": BIKING_SCOOTER_PACE}
    pace_input = input().lower()
    if pace_input not in dic:
        print("Invalid pace, try again")
    else:
        pace = dic[pace_input]
        break

print("Enter the earliest start time (e.g. 8:30am)")
while True:
    time_input = input()
    try:
        time_obj = datetime.strptime(time_input, "%I:%M%p")
        earliest_start = time_obj.hour * 60 + time_obj.minute
        break
    except Exception:
        print("Invalid time, try again")

print("Enter the latest end time time")
while True:
    time_input = input().strip()
    try:
        time_obj = datetime.strptime(time_input, "%I:%M%p")
        latest_end = time_obj.hour * 60 + time_obj.minute
        if latest_end <= earliest_start:
            print("Latest can not be earlier than earliest, try again")
            continue
        break
    except Exception:
        print("Invalid time, try again")
reqs = {"earliest_start": earliest_start,
        "latest_end": latest_end,
        "pace": pace}

print("Getting schedules...")
schedules = get_valid_schedules(courses, sections, reqs)
sorted = sort_highest_rated(schedules)
i = 0
n = 5
print(f"Showing {n} of {len(schedules)} schedules")
print("--------------------")
while i < len(sorted) and i<n:
    print_schedule(sorted[i])
    print("--------------------")
    i+=1
# course_inputs = input("Enter course or specific section id ('done' when finished):\n")
