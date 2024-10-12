import requests
from bs4 import BeautifulSoup
import utils

def safe_text(container, class_):
    find = container.find(class_=class_)
    if find:
        return find.get_text()
    else:
        return ""

def scrape_meeting(container):
    meeting = {}
    days = safe_text(container, "section-days")
    building = safe_text(container, "building-code")
    start_time = safe_text(container, "class-start-time")
    end_time = safe_text(container, "class-end-time")
    meeting["days"] = days
    meeting["building"] = building
    meeting["start_time"] = start_time
    meeting["end_time"] = end_time
    return meeting

def scrape_section(course_id, container):
    section_id = course_id + "-" + container.find(type="hidden").get("value")
    open_seats = safe_text(container, "open-seats-count")
    instructors = []
    instructor_containers = container.find_all(class_="section-instructor")
    for instructor_container in instructor_containers:
        instructors.append(instructor_container.get_text())
    meetings = []
    meeting_containers = container.find(class_="class-days-container").find_all(class_="row")
    for container in meeting_containers:
        meeting = scrape_meeting(container)
        meetings.append(meeting)
    section = {}
    section["course"] = course_id
    section["section_id"] = section_id
    section["meetings"] = meetings
    section["instructors"] = instructors
    section["open_seats"] = open_seats
    return section

def scrape_course(container):
    course_id = safe_text(container, "course-id")
    credits = safe_text(container, "course-min-credits")
    section_containers = container.find_all(class_="section delivery-f2f")
    sections = []
    for container in section_containers:
        section = scrape_section(course_id, container)
        sections.append(section)
    data = {}
    data["credits"] = credits
    data["sections"] = sections
    return data

def request_department(dept, semester):
    response = requests.get(f"https://app.testudo.umd.edu/soc/search?courseId={dept}&sectionId=&termId={semester}&_openSectionsOnly=on&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on")
    if response.status_code != 200:
        raise Exception(f"Could not access department {dept} for semester {semester}")
    soup = BeautifulSoup(response.content, "html.parser")
    courses_container = soup.find_all("div", class_="course")
    data = {}
    for container in courses_container:
        course_id = safe_text(container, "course-id")
        data[course_id] = scrape_course(container)
    return data

def request_all_departments(semester):
    response = requests.get("https://app.testudo.umd.edu/soc/")
    if response.status_code != 200:
        raise Exception(f"Could not access testudo")
    soup = BeautifulSoup(response.content, "html.parser")
    name_containers = soup.find_all(class_="prefix-abbrev push_one two columns")
    length = len(name_containers)
    all_data = {}
    i = 0
    for container in name_containers: 
        dept = container.get_text()
        data = request_department(dept, semester)
        all_data.update(data)
        i += 1
        percent = round(i/length*100)
        print(f"{i}/{length} complete ({percent}%)", end="\r", flush=True)
    return all_data


print("Requesting all department data from Testudo...")
data = request_all_departments("202501")
utils.write_data_to_json(data, "data/course_data_202501.json")
print()
print("Done")

