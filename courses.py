import re
from datetime import datetime
import utils

class Meeting:
    distance_data = utils.read_data_from_json("data/distance_data.json")

    def __init__(self, day, building, start_time, end_time):
        # int from 0-4, 0=Monday, ..., 4=Friday
        self.day = day
        self.building = building
        self.start_time = start_time
        self.end_time = end_time
    
    def print_meeting(self):
        print(f"Day: {self.day}")
        print(f"Building: {self.building}")
        print(f"Start time: {self.start_time}")
        print(f"End time: {self.end_time}")
    
    def time_gap(self, other):
        t1 = other.start_time - self.end_time
        t2 = self.start_time - other.end_time
        return max(t1, t2)

    def travel_time(self, other, pace_mph):
        if self.building not in self.distance_data or other.building not in self.distance_data:
            return 0
        distance_meters = self.distance_data[self.building][other.building]
        distance_miles = distance_meters*0.000621371
        time_hours = distance_miles/pace_mph
        return round(time_hours*60)
    
    def overlaps(self, other, pace):
        res = (self.time_gap(other) - self.travel_time(other, pace)) <= 0
        return res
    
    # block of form (start_time, end_time)
    def overlaps_block(self, block):
        return max(block[0] - self.end_time, self.start_time - block[1]) <= 0
    
class Section:
    professor_data = utils.read_data_from_json("data/professor_data.json")

    def __init__(self, credits, section_id=None, open_seats=None, instructors=None, meetings=None, data=None):
        self.earliest_start = 1440
        self.latest_end = 0
        self.credits = credits
        if data:
            self.section_id = data.get("section_id")
            self.open_seats = int(data.get("open_seats"))
            self.instructors = data.get("instructors")
            self.init_meetings_from_data(data.get("meetings"))
        else:
            self.section_id = section_id
            self.open_seats = open_seats
            self.instructors = instructors
            self.meetings = meetings
        self.init_instructor_rating()

    def init_meetings_from_data(self, all_meeting_data):
        self.meetings = [[] for _ in range(5)]
        self.meeting_strs = []

        for meeting_data in all_meeting_data:
            days_str = meeting_data.get("days")
            building = meeting_data.get("building")

            start_time = Section.str_time_to_int(meeting_data.get("start_time"))
            end_time = Section.str_time_to_int(meeting_data.get("end_time"))

            self.meeting_strs.append(f"{days_str} {meeting_data.get("start_time")}-{meeting_data.get("end_time")} {building}")

            self.earliest_start = min(self.earliest_start, start_time)
            self.latest_end = max(self.latest_end, end_time)

            days = re.findall("M|Tu|W|Th|F", days_str)
            day_to_int = {'M': 0, 'Tu': 1, 'W': 2, 'Th': 3, 'F': 4}
            for day in days:
                day_int = day_to_int.get(day)
                new_meeting = Meeting(day_int, building, start_time, end_time)
                self.meetings[day_int].append(new_meeting)

    def init_instructor_rating(self):
        rating_tot = 0
        for instructor in self.instructors:
            data = self.professor_data.get(instructor)
            if data is None or data.get("average_rating") is None:
                rating_tot += 3.0
            else:
                rating_tot += data.get("average_rating")
        if len(self.instructors) == 0:
            self.instructor_rating = 3.0
        else:
            self.instructor_rating = rating_tot/(len(self.instructors))

    def get_weighted_professor_rating(self):
        return self.credits * self.instructor_rating
    
    def str_time_to_int(time_str):
        if len(time_str) == 0:
            return -1
        time_obj = datetime.strptime(time_str, "%I:%M%p")
        return time_obj.hour * 60 + time_obj.minute

    def __str__(self):
        #meeting_str = ", ".join(self.meeting_strs)
        #return f"{self.section_id}\n└── {meeting_str}"
        return self.section_id

    def __len__(self):
        return len(self.meetings)



class Course:
    def __init__(self, course_id, credits=None, sections=None, data=None):
        if data:
            self.course_id = course_id
            self.credits = int(data.get("credits"))
            self.init_sections_from_data(data.get("sections"))
        else:
            self.course_id = course_id
            self.credits = credits
            self.sections = sections
    
    def init_sections_from_data(self, all_section_data):
        self.sections = []
        for section_data in all_section_data:
            section = Section(credits=self.credits, data=section_data)
            self.sections.append(section)

    def print_course(self):
        print(f"Course: {self.course_id}")
        for section in self.sections:
            section.print_section()
    
    def __len__(self):
        return len(self.sections)
    
