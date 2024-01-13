from flask import Flask, render_template, request, redirect, url_for, flash, session
import openai
import os

from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
import model


app = Flask(__name__)
app.config["SECRET_KEY"] = "Wfd8do6H7d74vdesbuRLlMFiAeXeJ7r"
# Flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "danger"


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def is_admin(self):
        return bool(session["User"]["is_admin"])

    def __repr__(self):
        return f"<{self.id}>"


@login_manager.user_loader
def load_user(userid):
    return User(userid)

openai.api_type = "azure"
openai.api_version = "2023-05-15" 
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # Your Azure OpenAI resource's endpoint value.
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
#--------------------Duyên: Chatbot--------------------------
@app.route("/chatbot")
@login_required
def chatbot():
    return render_template('chat.html')

@app.route('/get', methods=['POST'])
@login_required
def get_bot_response():
    message = request.form['msg']

    response = openai.ChatCompletion.create(
    engine="GPT35TURBO16K", # The deployment name you chose when you deployed the GPT-3.5-Turbo or GPT-4 model.
    messages = [
        {"role": "system", "content": "A teacher"},
        {"role": "user", "content": message},
    ])

    return str(response.choices[0].message.content)
#------------------------Duyên: END Chatbot-----------------------

@app.route("/")
@login_required
def index():
    success, message, student_course_list = model.get_student_course_list(
        current_user.id
    )
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    success, message, teacher_course_list = model.get_teacher_course_list(
        current_user.id
    )
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    return render_template(
        "index.html",
        teacher_course_list=teacher_course_list,
        student_course_list=student_course_list,
    )

@app.route("/chatbot")

@app.route("/remove_content/<int:CourseID>/<int:ContentID>")
@login_required
def remove_content(CourseID,ContentID):
    print(ContentID)
    success, message = model.remove_content(ContentID)
    if success:
        flash("Content removed successfully", "success")
    else:
        flash(message, "danger")
    return redirect(url_for("course", CourseID=CourseID))

@app.route("/remove_quiz/<int:CourseID>/<int:QuizID>")
@login_required
def remove_quiz(CourseID, QuizID):

    success, message = model.remove_quiz(QuizID)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for("course", CourseID=CourseID))


@app.route("/course/<int:CourseID>")
@login_required
def course(CourseID):
    success, message, is_teacher = model.is_teacher(current_user.id, CourseID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    success, message, course_data = model.get_course(CourseID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    if not course_data:
        flash("This course does not exist or you don't have access to it", "warning")
        return redirect(url_for("index"))
    success, message, content_list = model.get_content_list(CourseID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    success, message, quiz_list = model.get_quiz_list(CourseID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    return render_template(
        "course.html",
        is_teacher=is_teacher,
        course_data=course_data,
        content_list=content_list,
        quiz_list=quiz_list, # add list quiz
    )
@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are currently logged in", "primary")
        return redirect(url_for("index"))
    if request.method == "POST":
        Username = request.form.get("Username", "")
        Password = request.form.get("Password", "")
        success, message, raw_user = model.check_login(Username, Password)
        if success:
            login_user(User(raw_user["ID"]))
            session["User"] = raw_user
            success2, message2, is_manager = model.is_manager(current_user.id)
            if success2:
                session["User"]["is_manager"] = is_manager
            else:
                flash(message2, "warning")
                return redirect(url_for("login"))
            return redirect("/")
        else:
            flash(message, "warning")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        Username = request.form.get("Username", "")
        Password = request.form.get("Password", "")
        LastName = request.form.get("LastName", "")
        FirstName = request.form.get("FirstName", "")
        PhoneNumber = request.form.get("PhoneNumber", "")
        Email = request.form.get("Email", "")
        Faculty = request.form.get("Faculty", "")
        Institution = request.form.get("Institution", "")
        Address = request.form.get("Address", "")
        
        success, message = model.create_user(
            Username=Username,
            Password=Password,
            LastName=LastName,
            FirstName=FirstName,
            PhoneNumber=PhoneNumber,
            Email=Email,
            Faculty=Faculty,
            Institution=Institution,
            Address=Address,
        )
        if success:
            flash(
                "Your account has been created successfully, you can login now.",
                "success",
            )
            return redirect(url_for("login"))
        flash(message, "warning")
    return render_template("register.html")


@app.route("/users/")
@login_required
def user_list():
    success, message, user_list = model.get_user_list()
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    return render_template("user_list.html", user_list=user_list)


@app.route("/profile/<int:ID>/", methods=["GET", "POST"])
@login_required
def profile(ID):
    if request.method == "POST":
        Username = request.form.get("Username", "")
        LastName = request.form.get("LastName", "")
        FirstName = request.form.get("FirstName", "")
        PhoneNumber = request.form.get("PhoneNumber", "")
        Email = request.form.get("Email", "")
        Faculty = request.form.get("Faculty", "")
        Institution = request.form.get("Institution", "")
        Address = request.form.get("Address", "")
        success, message = model.edit_user_profile(
            ID=ID,
            Username=Username,
            LastName=LastName,
            FirstName=FirstName,
            PhoneNumber=PhoneNumber,
            Email=Email,
            Faculty=Faculty,
            Institution=Institution,
            Address=Address,
        )
        if success:
            flash(
                "Profile updated successfully.",
                "success",
            )
            return redirect(url_for("profile", ID=ID))
        flash(message, "warning")
    success, message, raw_user = model.get_user_profile(ID)
    if not success:
        flash(
            "No such user exists, or you don't have access to it's profile.", "warning"
        )
        return redirect(url_for("index"))
    success, message, course_list = model.get_all_course_list()
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    success, message, student_course_list = model.get_student_course_list(ID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    success, message, cluster_list = model.get_cluster_list(
        current_user.id, current_user.is_admin()
    )
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    success, message, user_cluster_list = model.get_cluster_list(ID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    return render_template(
        "profile.html",
        user=raw_user,
        course_list=course_list,
        student_course_list=student_course_list,
        cluster_list=cluster_list,
        user_cluster_list=user_cluster_list,
    )


@app.route("/clusters/", methods=["GET", "POST"])
@login_required
def cluster_list():
    if request.method == "POST":
        Name = request.form.get("Name", "DEFAULT")
        success, message = model.create_cluster(Name)
        if success:
            flash(message, "success")
            return redirect(url_for("cluster_list"))
        flash(message, "warning")
        return redirect(url_for("cluster_list"))
    success, message, cluster_list = model.get_cluster_list(
        current_user.id, current_user.is_admin()
    )
    if not success:
        flash(message, "warning")
        return redirect(url_for("cluster_list"))
    return render_template("cluster.html", cluster_list=cluster_list)


@app.route("/make_manager/<int:ManagerID>/", methods=["POST"])
@login_required
def make_manager(ManagerID):
    ClusterID = request.form.get("ClusterID", "")
    success, message = model.create_manager_cluster(ManagerID, ClusterID)
    if success:
        flash(message, "success")
    else:
        flash(message, "warning")
    return redirect(url_for("profile", ID=ManagerID))


@app.route("/courses/", methods=["GET", "POST"])
@login_required
def course_list():
    if request.method == "POST":
        Name = request.form.get("Name", "DEFAULT")
        ClusterID = request.form.get("ClusterID", "DEFAULT")
        TeacherID = request.form.get("TeacherID", "DEFAULT")
        success, message = model.create_course(Name, TeacherID, ClusterID)
        if success:
            flash(message, "success")
            return redirect(url_for("course_list"))
        flash(message, "warning")
        return redirect(url_for("course_list"))
    success, message, course_list = model.get_all_course_list()
    if not success:
        flash(message, "warning")
        return redirect(url_for("course_list"))
    success, message, cluster_list = model.get_cluster_list(
        current_user.id, current_user.is_admin()
    )
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    success, message, user_list = model.get_teacher_list()
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    return render_template(
        "course_list.html",
        course_list=course_list,
        cluster_list=cluster_list,
        user_list=user_list,
    )


@app.route("/participate/<int:StudentID>", methods=["POST"])
@login_required
def participate(StudentID):
    CourseID = request.form.get("CourseID", "")
    success, message = model.create_student_course(StudentID, CourseID)
    if success:
        flash(message, "success")
    else:
        flash(message, "warning")
    return redirect(url_for("profile", ID=StudentID))


@app.route("/students/<int:CourseID>/")
@login_required
def student_list(CourseID):
    success, message, student_list = model.get_course_student_list(CourseID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("course", CourseID=CourseID))
    return render_template("course_student.html", student_list=student_list)


@app.route("/newcontent/<int:CourseID>/", methods=["GET", "POST"])
@login_required
def new_content(CourseID):
    if request.method == "POST":
        Title = request.form.get("Title", "")
        TextContent = request.form.get("TextContent", "")
        success, message = model.create_content(CourseID, Title, TextContent)
        if success:
            flash("Content created successfully.", "success")
            return redirect(url_for("course", CourseID=CourseID))
        flash(message, "warning")
        return redirect(url_for("course", CourseID=CourseID))
    return render_template("new_content.html", CourseID=CourseID)

@app.route('/stop_students_viewing/<int:CourseID>/<int:QuizID>')
def stop_students_viewing(CourseID, QuizID):
    model.stop_students_viewing(QuizID)
    return redirect(url_for("course", CourseID=CourseID))

@app.route('/allow_students_viewing/<int:CourseID>/<int:QuizID>')
def allow_students_viewing(CourseID, QuizID):
    model.allow_students_viewing(QuizID)
    return redirect(url_for("course", CourseID=CourseID))

@app.route("/create_quizz/<int:CourseID>/", methods=["GET", "POST"])
def create_quizz(CourseID):
    if request.method == 'POST':
        title = request.form.get('Title')
        max_attempts= request.form.get("MaxAttempts")
        TeacherID=current_user.id
        quizz_id,success, message,  = model.create_quizz(CourseID, title, TeacherID,max_attempts)
        
        question_count = int(request.form.getlist('questionCounter')[-1])
        print(question_count)
        if not success:
            flash(message, "warning")
        questions = []
        for i in range(1,question_count+1):
            question_content = request.form.get(f'questions[{i}].content')
            question_type = request.form.get(f'questions[{i}].type')
            question_answer = request.form.get(f'questions[{i}].answer')
            
            num_options = int(request.form.get(f'questions[{i}].num_options', 0))

            if question_type == 'multiple_choice':
                options = request.form.getlist(f'questions[{i}].options[]')
            else:
                options = None

            question_data = {
                'content': question_content,
                'type': question_type,
                'answer': question_answer,
                'num_options': num_options,
                'options': options
            }

            questions.append(question_data)
        model.add_question_to_quiz(quizz_id,questions)

        return redirect(url_for("course", CourseID=CourseID))

    return render_template("create_quizzes.html", CourseID=CourseID)


@app.route("/view_quiz_responses/<int:CourseID>/<int:QuizID>/", methods=["GET","POST"])
@login_required
def view_quiz_responses(CourseID,QuizID):
    success, message, result_list = model.view_quiz_responses(CourseID,QuizID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("index"))
    return render_template("quiz_result.html", result_list=result_list)

@app.route("/quiz_responses/<int:CourseID>/<int:QuizID>/", methods=["GET","POST"])
@login_required
def quiz_responses(CourseID,QuizID):
    StudentID = current_user.id
    questions = []
    success, message, questions_data = model.get_question(QuizID)
    if not success:
        flash(message, "warning")
        return redirect(url_for("course", CourseID=CourseID))
    for question_data in questions_data:
        if question_data['QuestionType'] == 'multiple_choice':
            question_options = question_data['Options'].split('*')
            question_data['Options'] = question_options
        questions.append(question_data)
    if request.method == "POST":
        i=0
        j=1
        for question in questions:
            answers = request.form.get(f'answer{j}')
            j+=1
            if answers == question['CorrectAnswer']:
                score = 1
            else:
                score = 0
            success, message = model.save_responses(int(question['QuestionID']), StudentID, answers, score)
            
            if not success:
                flash(message, "warning")
                return redirect(url_for("course", CourseID=CourseID))
        flash(message, "success")
        return redirect(url_for("course", CourseID=CourseID))

    return render_template("quiz_responses.html", CourseID=CourseID, QuizID=QuizID, questions=questions)

def auto_grading(answers,correct_answer):
    score=1
    return score

if __name__ == '__main__':
    app.run(debug=True)