from courses import Course, Section
from functools import lru_cache

NORMAL_WALKING_PACE = 3
FAST_WALKING_PACE = 4
JOGGING_PACE = 6
BIKING_SCOOTER_PACE = 10
LITERALLY_TELEPORTING_PACE = 99999999

# Reads a particular course or section id from the data
# If found, returns a Section or Course object
# If not found, raises a KeyError
def read_course(input, data):
    input = input.upper()
    separated = input.split("-", 1)
    course_str = separated[0]
    if not course_str in data:
        raise KeyError(f"Invalid course {course_str}")
    course_data = data[course_str]
    if len(separated) > 1:
        for section in course_data.get("sections"):
            if section.get("section_id") == input:
                new_section = Section(credits=int(course_data.get("credits")), data=section)
                return new_section
        raise KeyError(f"Invalid section {input}")
    else:
        new_course = Course(course_id=course_str, data=course_data)
        return new_course

# Checks if two sections have overlapping meetings,
# based on the movement pace of the user
@lru_cache(maxsize=None)
def has_overlapping_meetings(s1, s2, pace):
    for i in range(5):
        for m1 in s1.meetings[i]:
            for m2 in s2.meetings[i]:
                if m1.overlaps(m2, pace):
                    return True
    return False

# Checks if a section overlaps the schedule
# based on the movement pace of the user
def overlaps_schedule(s1, schedule, pace):
    for s2 in schedule:
        if has_overlapping_meetings(s1, s2, pace):
            return True
    return False

# Checks if a section overlaps any of the blocks with form
# (start_time, end_time)
@lru_cache(maxsize=None)
def overlaps_blocks(s1, blocks):
    if blocks is None:
        return False
    for block in blocks:
        for i in range(5):
            for m1 in s1.meetings[i]:
                if m1.overlaps_block(block):
                    return True
    return False

# Checks to make sure that the section meets all the requirements
def meets_reqs(section, reqs):
    if section.open_seats == 0:
        return False
    if section.earliest_start < reqs.get("earliest_start") or section.latest_end > reqs.get("latest_end"):
        return False
    return True

# Recursive backtracking algorithm to find all possible combinations of sections
# We must have exactly one section from each course
# In addition, no section's meetings can overlap another section's meetings and all
# sections must meet the requirements specified in reqs
#
# reqs is a dictionary with keys for "pace", "earliest_start", "latest_end", and "blocks"
def get_valid_backtrack(courses, reqs, cur_schedule, valid_schedules, course_index):
    if course_index == len(courses):
        valid_schedules.append(cur_schedule[:])
        return
    course = courses[course_index]

    for section in course.sections:
        if meets_reqs(section, reqs) and not overlaps_schedule(section, cur_schedule, reqs.get("pace")) and not overlaps_blocks(section, reqs.get("blocks")):
            cur_schedule.append(section)
            get_valid_backtrack(courses, reqs, cur_schedule, valid_schedules, course_index+1)
            cur_schedule.pop()

# Gets all valid schedules based on desired courses, sections, and requirements
def get_valid_schedules(courses, sections, reqs):
    schedules = []
    get_valid_backtrack(courses, reqs, sections, schedules, 0)
    return schedules

# Gets the average professor rating for a schedule, weighted by credits per section
def get_average_rating_weighted(sections):
    rating_tot = 0
    credits_tot = 0
    for section in sections:
        rating_tot += section.get_weighted_professor_rating()
        credits_tot += section.credits
    return round(rating_tot/credits_tot, 3)

# Gets the first n schedules from a list of schedules
def get_n(schedules, n):
    return schedules[:n]

# Sorts a list of schedules by average professor rating, highest to lowest
def sort_highest_rated(schedules):
    return sorted(schedules, key=get_average_rating_weighted, reverse=True)

def print_schedule(schedule):
    for section in schedule:
        print(section)
    print(f"Average rating: {round(get_average_rating_weighted(schedule), 2)}")

