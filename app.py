import pickle
from flask import *
import utils
from courses import Course, Section
import schedule_builder_funcs as sb

app = Flask(__name__)
app.secret_key = "55029ed1d113712628567fa4fc2e9b00bc92c5cafc7965335c86aa9664c1c981"

all_course_data = utils.read_data_from_json("data/course_data_202501.json")
uniq_course_names = set()

name_i = 0

@app.route("/submit", methods=['POST'])
def course_submit():
    courses = []
    sections = []
    uniq_course_names = set()
    for i in range(1, 8): 
        name = request.form.get(f"course{str(i)}")
        if not name or len(name) < 2:
            continue
        course_name = (name.split("-", 1))[0].upper()
        if course_name in uniq_course_names:
            return redirect(url_for('index', error_msg=f"{course_name} repeated"))
        try:
            obj = sb.read_course(name, all_course_data)
        except KeyError as e:
            return redirect(url_for('index', error_msg=str(e)))
        if type(obj) == Course:
            courses.append(obj)
        elif type(obj) == Section:
            sections.append(obj)    
        uniq_course_names.add(course_name)
    pace_dic = {"normal": sb.NORMAL_WALKING_PACE,
                "fast": sb.FAST_WALKING_PACE,
                "running": sb.JOGGING_PACE,
                "scooter": sb.BIKING_SCOOTER_PACE}
    reqs = {"pace": pace_dic[request.form.get("pace")],
            "earliest_start": int(request.form.get("earliest-start")),
            "latest_end": int(request.form.get("latest-end"))}
    if len(courses) == 0 and len(sections) == 0:
        return redirect(url_for('index'))
    schedules = sb.get_valid_schedules(sections=sections, courses=courses, reqs=reqs)
    if len(schedules) == 0:
        return redirect(url_for('index', error_msg="No valid schedule found"))
    sorted_n = sb.get_n(sb.sort_highest_rated(schedules), 100)
    session["schedules"] = pickle.dumps(sorted_n)
    # error check if none
    return redirect(url_for('show_schedule', index=0))

@app.route("/", methods=['GET'])
def index():
    error_msg = request.args.get("error_msg")
    return render_template("hello.html", error_msg=error_msg)

@app.route("/view/<int:index>")
def show_schedule(index):
    schedules = pickle.loads(session.get("schedules", pickle.dumps([])))
    cur_schedule = schedules[index]
    average_rating = sb.get_average_rating_weighted(cur_schedule)
    average_rounded = round(average_rating, 2)
    return render_template("schedule.html", sections=cur_schedule, index=index, len=len(schedules), average_rating=average_rounded)
