import numpy as np
from password_strength import PasswordPolicy  # To check password strength
import json  # To receive values from javascript
import io  # provides access to files and directories
from PIL import Image, ImageDraw, ImageFont  # To create thumbnails
import syllables  # syllable estimator
from wtforms import FileField, SubmitField
from flask_wtf import FlaskForm  # Connect forms between html and flask
from require import login_required  # My own file in different location
from cs50 import SQL  # Harvard library SQL
import os  # used for  operating system functions
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session  # Sessions instead of web cookies
from flask import Flask, render_template, request, redirect, session, jsonify  # Flask
# Importing all libraries
# hashing passwords for protection
# Connect forms between html and flask

app = Flask(__name__)
# Security key for the application
app.config["SECRET_KEY"] = "read@blesecuritykey"
# For uploading folders in application location
app.config["UPLOAD_FOLDER"] = "static/files"
# Creating the flask form


class Uploadfiles(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload")


# Password Policy
policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=1,  # need min. 2 digits
    special=0,  # need min. 2 special characters
    # need min. 2 non-letter characters (digits, specials, anything)
    nonletters=0,
)

# Wait till HTML and CSS Loads
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Defining session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Defining the database
db = SQL("sqlite:///ReadableDB.db")

# Main page


@app.route("/")
def index():
    try:
        user_id = session["user_id"]  # get user id
        # get user email + username + password (cannot be used since its hashed)
        user_attr = db.execute("SELECT * FROM clients WHERE id = ?", user_id)
        user_attr = user_attr[0]
        username = user_attr["username"]  # get user username
        return render_template("home.html", username=username)
    except:
        return render_template("home.html")

# Signing up page


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    # If page entered normally (usually through button)
    if request.method == "GET":
        return render_template("signUp.html")
    else:  # After form submitted
        username = request.form.get("username")  # Get last name of user
        password = request.form.get("password")  # Get password of user
        confirm_password = request.form.get(
            "confirm_password")  # Get confirm password of user
        email = request.form.get("email")  # Get email of user
        flag = 0  # flag of user
        if not username:  # If user did not put last name
            return render_template("signUp.html", message="Please provide your username.")

        if not password:  # If user did not put password
            return render_template("signUp.html", message="Please provide your password.")

        if not check_password_strength(password):
            return render_template("signUp.html", message="Password is weak. Make sure it is at least 8 characters, one capital letter and one number.")

        if not confirm_password:  # If user did not confirm password
            return render_template("signUp.html", message="Please confirm your password.")

        if not email:  # If user did not put email
            return render_template("signUp.html", message="Please provide your email.")

        if password != confirm_password:  # If password is not equal to confirm_password
            return render_template("signUp.html", message="Password is not equal to confirmed password.")

        # hash the password for extra security
        hash = generate_password_hash(password)

        # Add person to database
        try:
            new_user = db.execute(
                "INSERT INTO clients (username, password, email) VALUES (?, ?, ?)", username, hash, email)
        except:
            return render_template("signUp.html", message="Username/Email already exists.")
        # Create new session for the user
        session["user_id"] = new_user

        return render_template("home.html", username=username)


def check_password_strength(password):
    # check if it passes all constraints
    if (len(policy.test(password))) == 0:
        return True
    else:
        return False

    # Login page


@ app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any previous sessions
    session.clear()
    # If page entered normally (usually through button)

    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")  # Get last name of user
        password = request.form.get("password")  # Get password of user
        if not username:  # If user did not put last name
            return render_template("login.html", message="Please provide your username.")

        if not password:  # If user did not put password
            return render_template("login.html", message="Please provide your password.")

        table_rows = db.execute(
            "SELECT * FROM clients WHERE username = ?", username)  # Look for username

        # if username is present check if hashed password is equal to password inserted
        if len(table_rows) != 1 or not check_password_hash(table_rows[0]["password"], password):
            return render_template("login.html", message="Invalid Username/Password")

        # Return user to their session
        session["user_id"] = table_rows[0]["id"]

        return render_template("home.html", username=username)

# Announcements Page


@app.route("/announcements", methods=["GET", "POST"])
@login_required
def announcements():
    # If page entered normally (usually through button)
    if request.method == "GET":
        return render_template("announcements.html")

# Logout user


@app.route("/logout")
def logout():
    # clear session to logout
    session.clear()

    return redirect("/")


@app.route("/pasteText", methods=["GET", "POST"])
@login_required
def paste_text():
    # If page entered normally (usually through button)
    if request.method == "GET":
        return render_template("pasteText.html")
    else:
        # get the title of the file chosen by the user
        name = request.form.get("title")
        # get the text pasted by the user
        pasted_text = request.form.get("pasted_text")
        user_id = session["user_id"]  # get the user ID
        # Change it to title format (capitalize each letter in start of new word)
        name = name.title()
        pasted_file_name = name + ".txt"  # Change the name to use in database
        # Open the file that has been chosen by the user
        pasted_file = open(pasted_file_name, "w", encoding="utf-8")
        pasted_file.write(pasted_text)  # paste in the pasted text
        pasted_file.close()  # close the file
        # read the file in bytes form
        pasted_file = open(pasted_file_name, "rb")
        blob_pasted_text = pasted_file.read()  # get text in blob format (bytes)
        pasted_file.close()  # Close file
        os.remove(pasted_file_name)  # remove the temp file created

        db.execute("INSERT INTO files (file_name,file_data,title,num,user_id) VALUES (?, ?, ?, ?, ?)",
                   pasted_file_name, blob_pasted_text, name, 0, user_id)  # paste everything into a database
        current_file_id = db.execute(
            "SELECT seq FROM sqlite_sequence WHERE name = ?", "files")
        current_file_id = current_file_id[0]
        current_file_id = current_file_id["seq"]
        number = current_file_id
        db.execute("UPDATE files SET num = ? WHERE id = ?", number, number)
        return redirect("/progressBar")  # go to progress bar page

# Upload File Function


@ app.route("/newSearch", methods=["GET", "POST"])
@login_required
def new_search():
    form = Uploadfiles()  # form defined at the top
    # If page entered normally (usually through button)
    if request.method == "GET":

        return render_template("newSearch.html", form=form)
    else:
        uploaded_file = form.file.data
        # check if a file is uploaded
        if (str(uploaded_file) != "<FileStorage: '' ('application/octet-stream')>"):
            # check if file is in .txt format
            if uploaded_file.filename.endswith(".txt"):
                user_id = session["user_id"]  # get user id
                # get file name without the ".txt"
                name = uploaded_file.filename.split(".")
                name = name[0].title()  # make the file name in title format

                db.execute("INSERT INTO files (file_name,file_data,title,num,user_id) VALUES (?, ?, ?, ?, ?)",
                           uploaded_file.filename, uploaded_file.stream.read(), name, 0, user_id)  # paste into database
                current_file_id = db.execute(
                    "SELECT seq FROM sqlite_sequence WHERE name = ?", "files")
                current_file_id = current_file_id[0]
                current_file_id = current_file_id["seq"]
                number = current_file_id
                db.execute(
                    "UPDATE files SET num = ? WHERE id = ?", number, number)
                return redirect("/progressBar")  # go to progress bar page
            else:
                # if file is not .txt
                return render_template("newSearch.html", message="Invalid file type", form=form)
        else:
            # if no file is inserted
            return render_template("newSearch.html", message="Insert file", form=form)


@app.route("/progressBar")
@login_required
def progress_bar():
    try:
        # When progress bar is called
        return render_template("progress.html", value=0)
    except:
        pass


def file_attr(content):
    words = count_words(content)  # Get words of file
    letters = count_letters(content)  # Get letters of file
    sentences = count_sentences(content)  # Get sentences of file
    syllables = count_syllables(content)  # Get syllables of file
    # Get complex words (3+ syllables) of file
    complex_words = count_complex_words(content)
    return words, letters, sentences, syllables, complex_words


def automated_readability_index(content):
    # List of keys for index
    readability_index_key = {"1": "Kindergarten",
                             "2": "1st or 2nd Grade",
                             "3": "3rd Grade",
                             "4": "4th Grade",
                             "5": "5th Grade",
                             "6": "6th Grade",
                             "7": "7th Grade",
                             "8": "8th Grade",
                             "9": "9th Grade",
                             "10": "10th Grade",
                             "11": "11th Grade",
                             "12": "12th Grade",
                             "13": "College Student",
                             "14": "Professor", }
    words = count_words(content)  # Get words
    letters = count_letters(content)  # Get letters
    sentences = count_sentences(content)  # Get sentences
    score = "0"  # initialize score
    index = 0  # initialize index
    try:
        index = round(4.71 * (letters/words) + 0.5 *
                      (words/sentences) - 21.43)  # Index calculation
        for key in readability_index_key.keys():  # loop through dictionary keys
            if str(index) == key:  # if index is equal to key
                score = readability_index_key[key]  # score = value of key
            elif int(index) < 1:
                score = "Pre-KG"
            elif int(index) > 14:
                score = "Professor"
    except:
        score = "N/A"

    return str(index), score


def gunning_fog_index(content):
    # Index key
    fog_key = {"20+": "Post-Graduate Plus",
               "17": "Post-Graduate",
               "16": "College Senior",
               "15": "College Junior",
               "14": "College Sophomore",
               "13": "College Freshman",
               "12": "High School Senior",
               "11": "High School Junior",
               "10": "High School Sophomore",
               "9": "High School Freshman",
               "8": "8th Grade",
               "7": "7th Grade",
               "6": "6th Grade",
               "5": "5th Grade",
               "4": "4th Grade",
               "3": "3rd Grade",
               "2": "2nd Grade",
               "1": "1st Grade", }
    words = count_words(content)  # Get words
    sentences = count_sentences(content)  # Get sentences
    # get complex words (3+ syllables)
    complex_words = count_complex_words(content)
    grade = "0"  # initialize grade
    index = 0  # initialize index
    try:
        # Index calculation
        index = round(0.4 * ((words/sentences) + 100 * (complex_words/words)))
        if (index > 20):  # Check index range and compare it to key
            grade = fog_key["20+"]
        elif(17 <= index < 21):
            grade = fog_key["17"]
        elif(index == 17):
            grade = fog_key["17"]
        elif(index == 16):
            grade = fog_key["16"]
        elif(index == 15):
            grade = fog_key["15"]
        elif(index == 14):
            grade = fog_key["14"]
        elif(index == 13):
            grade = fog_key["13"]
        elif(index == 12):
            grade = fog_key["12"]
        elif(index == 11):
            grade = fog_key["11"]
        elif(index == 10):
            grade = fog_key["10"]
        elif(index == 9):
            grade = fog_key["9"]
        elif(index == 8):
            grade = fog_key["8"]
        elif(index == 7):
            grade = fog_key["7"]
        elif(index == 6):
            grade = fog_key["6"]
        elif(index == 5):
            grade = fog_key["5"]
        elif(index == 4):
            grade = fog_key["4"]
        elif(index == 3):
            grade = fog_key["3"]
        elif(index == 2):
            grade = fog_key["2"]
        elif(index == 1):
            grade = fog_key["1"]
        elif(index < 1):
            grade = "Kindergarten"
    except:
        grade = "N/A"

    return str(index), grade


def flesch_kincaid_reading_ease(content):
    # Index key
    flesch_key = {"100": "5th Grade",
                  "89": "6th Grade",
                  "79": "7th Grade",
                  "69": "8th & 9th Grade",
                  "59": "10th to 12th Grade",
                  "49": "College",
                  "29": "College Graduate",
                  "9": "Professional"}
    words = count_words(content)  # get words
    sentences = count_sentences(content)  # get sentences
    syllable = count_syllables(content)  # get syllables
    grade = "0"  # initialize grade
    index = 0  # initialize index
    try:
        index = round(206.835 - 1.015 * (words/sentences) -
                      84.6 * (syllable/words))  # calculate index
        if (90 <= index <= 100):  # check index with key
            grade = flesch_key["100"]
        elif(80 <= index < 90):
            grade = flesch_key["89"]
        elif(70 <= index < 80):
            grade = flesch_key["79"]
        elif(60 <= index < 70):
            grade = flesch_key["69"]
        elif(50 <= index < 60):
            grade = flesch_key["59"]
        elif(30 <= index < 50):
            grade = flesch_key["49"]
        elif(10 <= index < 30):
            grade = flesch_key["29"]
        elif(0 <= index < 10):
            grade = flesch_key["9"]
        elif (index < 0):
            grade = "Professional"
        else:
            grade = "4th Grade"
    except:
        grade = "N/A"
    return str(index), grade

# Coleman Liau Index


def liau_index(content):
    # Index key
    liau_key = {"1": ["1st Grade", "~7-8"],
                "2": ["2nd Grade", "~8-9"],
                "3": ["3rd Grade", "~9-10"],
                "4": ["4th Grade", "~10-11"],
                "5": ["5th Grade", "~11-12"],
                "6": ["6th Grade", "~12-13"],
                "7": ["7th Grade", "~13-14"],
                "8": ["8th Grade", "~14-15"],
                "9": ["9th Grade", "~15-16"],
                "11": ["11th Grade", "~16-17"],
                "12": ["12th Grade", "~17-18"]}
    letters = count_letters(content)  # get letters
    words = count_words(content)  # get words
    sentences = count_sentences(content)  # get sentences
    grade = "0"  # initialize grade
    age = "0"  # initialize age
    index = 0  # initialize index
    try:
        index = round(5.89 * (letters / words) -
                      0.3 * (sentences / words) - 15.8)  # calculate index
        for key in liau_key.keys():  # loop through key keys
            if str(index) == key:
                values = liau_key[key]  # value = key value
                grade = values[0]  # grade = key value
                age = values[1]  # age = key value
        if (grade == "0") and (age == "0"):  # if outside keys
            if (index > 12):
                grade = "Grade 12+"
                age = "18+"
            else:
                grade = "Grade 0"
                age = "< 7"
    except:
        grade = "N/A"
        age = "N/A"

    return str(index), grade, age


def count_letters(content):
    content = str(content)  # Turn file content to string
    letters = 0  # initialize letters
    for i in range(len(content)):  # loop through the length of the file content
        if (content[i].isalpha()):  # check if the letter in the file content is a letter
            letters += 1  # add to the letters variable
    return letters


def count_words(content):
    content = str(content)  # Turn file content to string
    words = 1  # initialize words
    for i in range(len(content)):  # loop through the length of the file content
        if (content[i].isspace()):  # check if there is a space and count that as a word
            words += 1
    return words


def count_sentences(content):
    content = str(content)  # turn file content to a string
    sentences = 0  # initialize sentences
    for i in range(len(content)):
        # if a period, !, ? is present count that as a sentence
        if ((content[i] == ".") or (content[i] == "!") or (content[i] == "?")):
            sentences += 1
    return sentences


def count_syllables(content):
    content = str(content)  # turn file content to a string
    syllable = 0  # initialize syllables
    for word in content.split():  # split each word
        # use syllables library to estimate number of syllables in a word
        syllable += syllables.estimate(word)
    return syllable


def count_complex_words(content):
    content = str(content)  # turn file content to a string
    complex_words = 0  # initialize complex words
    for word in content.split():  # for each word in the pasted text
        syllable = 0  # initialize syllables
        # use syllables library to estimate number of syllables in a word and turn it to an int
        syllable += int(syllables.estimate(word))
        if syllable >= 3:  # if syllables in the word is more than three count that as a complex word
            complex_words += 1
    return complex_words


@ app.route("/readability")
@ login_required
def readability_grades():

    # Manipulate files
    file_id = db.execute(
        "select seq from sqlite_sequence where name= ?", "files")  # get most recent file id
    file_id = file_id[0]  # get most recent file id
    file_id = file_id["seq"]  # get most recent file id
    content = db.execute(
        "SELECT file_data FROM files where id = ?", file_id)  # get content of most recent file
    file_title = db.execute(
        "SELECT file_name FROM files where id = ?", file_id)  # get name of most recent file
    file_title = file_title[0]  # get name of most recent file
    file_title = file_title["file_name"]  # get name of most recent file
    if file_title.endswith(".txt"):  # if file ends with .txt
        file_title = file_title.split(".")  # remove the .txt
        file_title = file_title[0].upper()  # turn it all to uppercase
    content = content[0]  # get file content
    content = content["file_data"]  # get file content
    # turn blob (bytes) file content to string
    content = content.decode('utf-8', "ignore")
    # remove any new lines in links and regular new line syntax
    content = content.replace("\r\n", " ")
    # remove any new lines in links and regular new line syntax
    content = content.replace("\n", " ")
    # get grades
    liau_index_ans, grade_liau, age_liau = liau_index(
        content)  # call index 1 and get values
    flesch_kincaid_reading_ease_ans, grade_flesch = flesch_kincaid_reading_ease(
        content)  # call index 2 and get values
    gunning_fog_index_ans, grade_gunning_fog = gunning_fog_index(content)
    automated_readability_index_ans, grade_automated_readability = automated_readability_index(
        content)  # call index 3 and get values
    words, letters, sentences, syllables, complex_words = file_attr(
        content)  # call index 4 and get values
    recommended_level = generate_level(
        grade_liau, grade_flesch, grade_gunning_fog, grade_automated_readability)  # generate the recommended level
    # insert all index values to database
    db.execute("INSERT INTO sequences (words,letters,sentences,syllables,complex_words, liau_index, liau_age, liau_grade, flesch_kincaid_index, flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level, file_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", int(
        words), int(letters), int(sentences), int(syllables), int(complex_words), int(liau_index_ans), str(age_liau), str(grade_liau), int(flesch_kincaid_reading_ease_ans), str(grade_flesch), int(gunning_fog_index_ans), str(grade_gunning_fog), int(automated_readability_index_ans), str(grade_automated_readability), recommended_level, file_id)
    # Create history thumbnail
    # initialize font for image
    font = ImageFont.truetype("static/ChunkFive-Regular.otf", 18)
    # use template for background
    history_thumbnail = Image.open("static/history book bg.png")
    drawer = ImageDraw.Draw(history_thumbnail)  # draw image
    # draw title at the center of the image
    bbox = drawer.textbbox((0, 0), file_title, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    drawer.text(((300-w)/2, (300-h)/2), file_title,
                fill="black", font=font)  # draw
    history_thumbnail.save("waste.png")  # save image temporarily
    filename = "waste.png"
    with open(filename, 'rb') as file:  # open temp image
        thumbnail = file.read()  # read image
    db.execute(
        "UPDATE files SET history_image = ? WHERE id = ?", thumbnail, file_id)  # store image as blob (bytes) in database
    os.remove("waste.png")  # delete image
    # Return tempplate

    return render_template("readability.html", recommended_level=recommended_level, score1=liau_index_ans, score2=flesch_kincaid_reading_ease_ans, score3=gunning_fog_index_ans, score4=automated_readability_index_ans, grade4=grade_automated_readability, grade3=grade_gunning_fog, grade2=grade_flesch, grade1=grade_liau, age1=age_liau, words=words, sentences=sentences, syllables=syllables, complex_words=complex_words, letters=letters)


def generate_level(index1, index2, index3, index4):
    numbers = []  # Initialize numbers list
    # create index key if grade is a string
    index_key = {"College Student": 13,
                 "Professor": 15,
                 "Post-Graduate Plus": 14,
                 "Post-Graduate": 14,
                 "College Senior": 13,
                 "College Junior": 13,
                 "College Sophomore": 13,
                 "College Freshman": 13,
                 "High School Senior": 12,
                 "High School Junior": 11,
                 "High School Sophomore": 10,
                 "High School Freshman": 9,
                 "College": 13,
                 "College Graduate": 14,
                 "Professional": 15,
                 }
    # if the recommended grade is greater than 12
    final_key = {"College Student": 13,
                 "Post-Graduate": 14,
                 "Professor": 15,
                 }
    # create index list of all grades
    index = [index1, index2, index3, index4]

    # loop through index list
    for i in range(len(index)):
        # loop through all keys in the index_key dictionary
        for key in index_key.keys():
            # check if grade is a string and is equal to the key
            if index[i] == key:
                # append the value of the key to numbers list
                numbers.append(index_key[key])
    # loop through every grade in index list
    for grade in index:
        # loop through every character in the grade
        for char in grade:
            # check if there is a number - such as 5th grade the "5" is the number
            if char.isdigit():
                # append to the numbers list
                numbers.append(int(char))
    # find the mean of all the grades
    numbers_excluding_outliers = remove_outliers(numbers)
    try:
        recommended_grade = round(
            (sum(numbers_excluding_outliers))/len(numbers_excluding_outliers))
    except:
        recommended_grade = 0
    # check if the recommended_grade is between 16 and 12
    if 12 < recommended_grade < 16:
        # loop through every key in the dictionary
        for key in final_key.keys():
            # check if the recommended grade is equal to the value of the key being looped
            if recommended_grade == final_key[key]:
                recommended_grade = key
    # if the recommended_grade is more than 16
    elif recommended_grade >= 16:
        recommended_grade = "Professor"
    return str(recommended_grade)


def remove_outliers(numbers):

    upper_bound = np.percentile(numbers, 75)  # find upper bound
    lower_bound = np.percentile(numbers, 25)  # find lower bound
    # get the range between upper and lower and multiply by 0.3 to make the range smaller
    inter_quartile_range = (upper_bound - lower_bound) * 1.5
    bound_sets = (abs(round(inter_quartile_range - lower_bound)),
                  round(upper_bound + inter_quartile_range))  # create bound sets for upper and lower bound
    numbers_excluding_outliers = []  # initialize numbers without outliers list
    for number in numbers:
        if ((number > bound_sets[0]) and (number < bound_sets[1])):
            # if the number is not in the bounds
            numbers_excluding_outliers.append(number)
    return numbers_excluding_outliers


@ app.route("/findText")
@ login_required
def find_text():
    file_id_total = db.execute(
        "select seq from sqlite_sequence where name= ?", "samples")  # Select how many samples are present in database
    file_id_total = file_id_total[0]
    file_id_total = file_id_total["seq"]
    counter = 1  # initialize counter variable
    file_names = []  # initialize file-names list
    ids = []  # initialize ids list
    for i in range(file_id_total):  # loop through
        current_file_name = db.execute(
            "SELECT names FROM samples WHERE id = ?", i+1)  # select names of sample
        current_file_name = current_file_name[0]
        current_file_name = current_file_name["names"]
        file_names.append(current_file_name)
        ids.append(counter)
        counter += 1
    # return page
    return render_template("findText.html", file_names=zip(file_names, ids))


@ app.route("/findTextImage", methods=["GET", "POST"])
@ login_required
def find_text_image():
    if request.method == "GET":
        # redirect to find text page
        return redirect("/findText")
    # get from json id of image pressed
    text_image_scope_id = int(request.get_json())
    file_name = db.execute(
        "SELECT names FROM samples where id = ?", text_image_scope_id)  # search for id in database
    # get file name + manipulate file name style
    file_name = file_name[0]
    file_name = file_name["names"]
    file_name = file_name.upper()
    # search for all index values for file
    file_attributes = db.execute(
        "SELECT * FROM samples WHERE id = ?", text_image_scope_id)
    # split all values into different variables
    file_attributes = file_attributes[0]
    liau_index = file_attributes["liau_index"]
    liau_age = file_attributes["liau_age"]
    liau_grade = file_attributes["liau_grade"]
    flesch_kincaid_index = file_attributes["flesch_kincaid_index"]
    flesch_kincaid_grade = file_attributes["flesch_kincaid_grade"]
    gunning_fog_index = file_attributes["gunning_fog_index"]
    gunning_fog_grade = file_attributes["gunning_fog_grade"]
    automated_readability_index = file_attributes["automated_readability_index"]
    automated_readability_grade = file_attributes["automated_readability_grade"]
    words = file_attributes["words"]
    letters = file_attributes["letters"]
    sentences = file_attributes["sentences"]
    syllables = file_attributes["syllables"]
    complex_words = file_attributes["complex_words"]
    recommended_level = file_attributes["recommended_level"]
    return jsonify(render_template("textImage.html", recommended_level=recommended_level, file_name=file_name, flesch_kincaid_index=flesch_kincaid_index, flesch_kincaid_grade=flesch_kincaid_grade, liau_index=liau_index, liau_age=liau_age, liau_grade=liau_grade, gunning_fog_index=gunning_fog_index, gunning_fog_grade=gunning_fog_grade, automated_readability_index=automated_readability_index, automated_readability_grade=automated_readability_grade, words=words, letters=letters, sentences=sentences, syllables=syllables, complex_words=complex_words,))


@ app.route("/sortImageAZ", methods=["POST"])
@ login_required
def sort_image():
    file_id_total = db.execute(
        "select seq from sqlite_sequence where name= ?", "samples")  # select how many samples are present
    file_id_total = file_id_total[0]
    file_id_total = file_id_total["seq"]
    # Bubble Sort (Ascending)
    # Gets all data from database
    sort_image = db.execute("SELECT * FROM samples")
    for i in range(file_id_total):  # bubble sort loop 1
        for j in range(file_id_total-1):  # bubble sort loop 2
            file_1 = sort_image[j]  # gets the first row from the database
            file_2 = sort_image[j+1]  # gets second row from database
            # compares the value of the key "names"
            if (file_1['names'] > file_2['names']) == True:
                temp = sort_image[j]  # puts first value in temp variable
                sort_image[j] = sort_image[j+1]  # switches value
                # puts temp in second value or first in second value
                sort_image[j+1] = temp

    for i in range(file_id_total):
        file_attributes = sort_image[i]
        # get all file attributes from current file
        name = file_attributes["names"]
        liau_index = file_attributes["liau_index"]
        liau_age = file_attributes["liau_age"]
        liau_grade = file_attributes["liau_grade"]
        flesch_kincaid_index = file_attributes["flesch_kincaid_index"]
        flesch_kincaid_grade = file_attributes["flesch_kincaid_grade"]
        gunning_fog_index = file_attributes["gunning_fog_index"]
        gunning_fog_grade = file_attributes["gunning_fog_grade"]
        automated_readability_index = file_attributes["automated_readability_index"]
        automated_readability_grade = file_attributes["automated_readability_grade"]
        words = file_attributes["words"]
        letters = file_attributes["letters"]
        sentences = file_attributes["sentences"]
        syllables = file_attributes["syllables"]
        complex_words = file_attributes["complex_words"]
        recommended_level = file_attributes["recommended_level"]
        # update row in table
        db.execute("UPDATE samples SET names = ?, words = ?, letters = ?, sentences = ?, syllables = ?, complex_words = ?, liau_index = ?, liau_age = ?, liau_grade = ?, flesch_kincaid_index = ?, flesch_kincaid_grade = ?, gunning_fog_index = ?, gunning_fog_grade = ?, automated_readability_index = ?, automated_readability_grade = ?, recommended_level = ? WHERE id = ?",
                   name, words, letters, sentences, syllables, complex_words, liau_index, liau_age, liau_grade, flesch_kincaid_index, flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level, i+1)
    return jsonify(render_template("findText.html"))


@ app.route("/sortImageZA", methods=["POST"])
@ login_required
def sort_image_desc():
    file_id_total = db.execute(
        "select seq from sqlite_sequence where name= ?", "samples")  # select how many samples are present
    file_id_total = file_id_total[0]
    file_id_total = file_id_total["seq"]
    # Bubble Sort (Descending)
    # Gets all data from database
    sort_image = db.execute("SELECT * FROM samples")
    for i in range(file_id_total):  # bubble sort loop 1
        for j in range(file_id_total-1):  # bubble sort loop 2
            file_1 = sort_image[j]  # gets the first row from the database
            file_2 = sort_image[j+1]  # gets second row from database
            # compares the value of the key "names"
            if (file_1['names'] > file_2['names']) == False:
                temp = sort_image[j]  # puts first value in temp variable
                sort_image[j] = sort_image[j+1]  # switches value
                # puts temp in second value or first in second value
                sort_image[j+1] = temp

    for i in range(file_id_total):
        file_attributes = sort_image[i]
        # get all file attributes from current file
        name = file_attributes["names"]
        liau_index = file_attributes["liau_index"]
        liau_age = file_attributes["liau_age"]
        liau_grade = file_attributes["liau_grade"]
        flesch_kincaid_index = file_attributes["flesch_kincaid_index"]
        flesch_kincaid_grade = file_attributes["flesch_kincaid_grade"]
        gunning_fog_index = file_attributes["gunning_fog_index"]
        gunning_fog_grade = file_attributes["gunning_fog_grade"]
        automated_readability_index = file_attributes["automated_readability_index"]
        automated_readability_grade = file_attributes["automated_readability_grade"]
        words = file_attributes["words"]
        letters = file_attributes["letters"]
        sentences = file_attributes["sentences"]
        syllables = file_attributes["syllables"]
        complex_words = file_attributes["complex_words"]
        recommended_level = file_attributes["recommended_level"]
        # update row in table
        db.execute("UPDATE samples SET names = ?, words = ?, letters = ?, sentences = ?, syllables = ?, complex_words = ?, liau_index = ?, liau_age = ?, liau_grade = ?, flesch_kincaid_index = ?, flesch_kincaid_grade = ?, gunning_fog_index = ?, gunning_fog_grade = ?, automated_readability_index = ?, automated_readability_grade = ?, recommended_level = ? WHERE id = ?",
                   name, words, letters, sentences, syllables, complex_words, liau_index, liau_age, liau_grade, flesch_kincaid_index, flesch_kincaid_grade, gunning_fog_index, gunning_fog_grade, automated_readability_index, automated_readability_grade, recommended_level, i+1)
    return jsonify(render_template("findText.html"))

# Sorting


@ app.route("/sortImageZAH", methods=["POST"])
@ login_required
def sort_image_desc_history():
    file_id_total = db.execute(
        "select seq from sqlite_sequence where name= ?", "files")
    file_id_total = file_id_total[0]
    file_id_total = file_id_total["seq"]
    # Bubble Sort (Descending)
    # Gets all data from database
    sort_image = db.execute("SELECT * FROM files")
    sort_image_sequences = db.execute("SELECT * FROM sequences")
    for i in range(file_id_total):  # bubble sort loop 1
        for j in range(file_id_total-1):  # bubble sort loop 2
            file_1 = sort_image[j]  # gets the first row from the database
            file_2 = sort_image[j+1]  # gets second row from database
            # compares the value of the key "names"
            if (file_1['file_name'] > file_2['file_name']) == False:
                temp = sort_image[j]  # puts first value in temp variable
                temp2 = sort_image_sequences[j]
                sort_image[j] = sort_image[j+1]  # switches value
                # switches value
                sort_image_sequences[j] = sort_image_sequences[j+1]
                # puts temp in second value or first in second value
                sort_image[j+1] = temp
                sort_image_sequences[j+1] = temp2

    for i in range(file_id_total):
        file_attributes = sort_image[i]
        sequence_attributes = sort_image_sequences[i]
        file_name = file_attributes["file_name"]
        file_data = file_attributes["file_data"]
        file_number = file_attributes["num"]
        title = file_attributes["title"]
        history_image = file_attributes["history_image"]
        user_id = file_attributes["user_id"]
        file_words = sequence_attributes["words"]
        file_letters = sequence_attributes["letters"]
        file_sentences = sequence_attributes["sentences"]
        file_syllables = sequence_attributes["syllables"]
        file_complex_words = sequence_attributes["complex_words"]
        file_liau_index = sequence_attributes["liau_index"]
        file_liau_age = sequence_attributes["liau_age"]
        file_liau_grade = sequence_attributes["liau_grade"]
        file_flesch_kincaid_index = sequence_attributes["flesch_kincaid_index"]
        file_flesch_kincaid_grade = sequence_attributes["flesch_kincaid_grade"]
        file_gunning_fog_index = sequence_attributes["gunning_fog_index"]
        file_gunning_fog_grade = sequence_attributes["gunning_fog_grade"]
        file_automated_readability_index = sequence_attributes["automated_readability_index"]
        file_automated_readability_grade = sequence_attributes["automated_readability_grade"]
        file_recommended_level = sequence_attributes["recommended_level"]
        file_id = sequence_attributes["file_id"]
        db.execute("UPDATE sequences SET words = ?, letters = ?, sentences = ?, syllables = ?, complex_words = ?, liau_index = ?, liau_age = ?, liau_grade = ?, flesch_kincaid_index = ?, flesch_kincaid_grade = ?, gunning_fog_index = ?, gunning_fog_grade = ?, automated_readability_index = ?, automated_readability_grade = ?, recommended_level = ?, file_id = ? WHERE id = ?",
                   file_words, file_letters, file_sentences, file_syllables, file_complex_words, file_liau_index, file_liau_age, file_liau_grade, file_flesch_kincaid_index, file_flesch_kincaid_grade, file_gunning_fog_index, file_gunning_fog_grade, file_automated_readability_index, file_automated_readability_grade, file_recommended_level, file_id, i+1)
        db.execute("UPDATE files SET file_name = ?, file_data = ?, title = ?, history_image = ?, num = ?, user_id = ? WHERE id = ?",
                   file_name, file_data, title, history_image, file_number, user_id, i+1)
    return jsonify(render_template("history.html"))


@ app.route("/sortImageAZH", methods=["POST"])
@ login_required
def sort_image_history():
    file_id_total = db.execute(
        "select seq from sqlite_sequence where name= ?", "files")
    file_id_total = file_id_total[0]
    file_id_total = file_id_total["seq"]
    # Bubble Sort (Ascending)
    # Gets all data from database
    sort_image = db.execute("SELECT * FROM files")
    sort_image_sequences = db.execute("SELECT * FROM sequences")
    for i in range(file_id_total):  # bubble sort loop 1
        for j in range(file_id_total-1):  # bubble sort loop 2
            file_1 = sort_image[j]  # gets the first row from the database
            file_2 = sort_image[j+1]  # gets second row from database
            # compares the value of the key "names"
            if (file_1['file_name'] > file_2['file_name']) == True:
                temp = sort_image[j]  # puts first value in temp variable
                temp2 = sort_image_sequences[j]
                sort_image[j] = sort_image[j+1]  # switches value
                # switches value
                sort_image_sequences[j] = sort_image_sequences[j+1]
                # puts temp in second value or first in second value
                sort_image[j+1] = temp
                sort_image_sequences[j+1] = temp2

    for i in range(file_id_total):
        # get all file attributes
        file_attributes = sort_image[i]
        sequence_attributes = sort_image_sequences[i]
        file_name = file_attributes["file_name"]
        file_data = file_attributes["file_data"]
        file_number = file_attributes["num"]
        title = file_attributes["title"]
        history_image = file_attributes["history_image"]
        user_id = file_attributes["user_id"]
        # update table
        file_words = sequence_attributes["words"]
        file_letters = sequence_attributes["letters"]
        file_sentences = sequence_attributes["sentences"]
        file_syllables = sequence_attributes["syllables"]
        file_complex_words = sequence_attributes["complex_words"]
        file_liau_index = sequence_attributes["liau_index"]
        file_liau_age = sequence_attributes["liau_age"]
        file_liau_grade = sequence_attributes["liau_grade"]
        file_flesch_kincaid_index = sequence_attributes["flesch_kincaid_index"]
        file_flesch_kincaid_grade = sequence_attributes["flesch_kincaid_grade"]
        file_gunning_fog_index = sequence_attributes["gunning_fog_index"]
        file_gunning_fog_grade = sequence_attributes["gunning_fog_grade"]
        file_automated_readability_index = sequence_attributes["automated_readability_index"]
        file_automated_readability_grade = sequence_attributes["automated_readability_grade"]
        file_recommended_level = sequence_attributes["recommended_level"]
        file_id = sequence_attributes["file_id"]
        db.execute("UPDATE sequences SET words = ?, letters = ?, sentences = ?, syllables = ?, complex_words = ?, liau_index = ?, liau_age = ?, liau_grade = ?, flesch_kincaid_index = ?, flesch_kincaid_grade = ?, gunning_fog_index = ?, gunning_fog_grade = ?, automated_readability_index = ?, automated_readability_grade = ?, recommended_level = ?, file_id = ? WHERE id = ?",
                   file_words, file_letters, file_sentences, file_syllables, file_complex_words, file_liau_index, file_liau_age, file_liau_grade, file_flesch_kincaid_index, file_flesch_kincaid_grade, file_gunning_fog_index, file_gunning_fog_grade, file_automated_readability_index, file_automated_readability_grade, file_recommended_level, file_id, i+1)
        db.execute("UPDATE files SET file_name = ?, file_data = ?, title = ?, history_image = ?, num = ?, user_id = ? WHERE id = ?",
                   file_name, file_data, title, history_image, file_number, user_id, i+1)
    return jsonify(render_template("history.html"))


@ app.route("/history", methods=["GET", "POST"])
@ login_required
def history():
    delete_flag = True  # flag
    numbers = []  # initialize numbers list
    history_imgs = []  # initialize history numbers list
    the_ids = []  # initialize Ids list
    user_id = session["user_id"]  # get user id
    try:
        # find most recent file id
        file_id_total = db.execute(
            "select seq from sqlite_sequence where name= ?", "files")
        file_id_total = file_id_total[0]
        file_id_total = file_id_total["seq"]
        # delete image from pc
        if (delete_flag == False):
            os.chdir(r"E:\Mohe\Desktop\Code\IB CS\Internal\static\files")
            all_files = os.listdir()
            for f in all_files:
                os.remove(f)
            delete_flag = True
    except:
        pass
    try:
        counter = 0  # initialize counter
        for i in range(file_id_total):  # loop through total amount of ids present in database
            # get file id that has an history image and belongs to the user logged in
            file_id = db.execute(
                "SELECT id FROM files WHERE history_image IS NOT NULL AND user_id = ?", user_id)
            # get the ids and paste them in list
            ids = [x.get("id") for x in file_id]
            for sqlid in ids:  # loop through all ids extracted for user
                counter += 1
                file_id = sqlid  # get current id in loop
                numbers.append(counter)  # append id count
                the_ids.append(file_id)  # append id
                # get history image
                image = db.execute(
                    "SELECT history_image FROM files where id = ?", file_id)
                image = image[0]
                image = image["history_image"]
                dataBytesIO = io.BytesIO(image)
                img = Image.open(dataBytesIO)
                img = img.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], f"trash{sqlid}.png"))
                img = os.path.join(
                    app.config['UPLOAD_FOLDER'], f"trash{sqlid}.png")
                history_imgs.append(img)
            delete_flag = False
            # zip used in order to loop through both lists in html
            return render_template("history.html", image=history_imgs, numbers=zip(numbers, the_ids))
    except:
        return render_template("history.html", image=history_imgs, numbers=zip(numbers, the_ids))


@ app.route("/historyImage", methods=["GET", "POST"])
@ login_required
def history_scope():
    if request.method == "GET":
        return redirect("/history")
    history_image_scope_id = int(request.get_json())  # get image id
    # get file name
    file_number = db.execute(
        "SELECT num FROM files where id = ?", history_image_scope_id)
    file_number = file_number[0]
    file_number = file_number["num"]
    file_name = db.execute(
        "SELECT file_name FROM files where num = ?", file_number)
    file_name = file_name[0]
    file_name = file_name["file_name"]
    if file_name.endswith(".txt"):
        file_name = file_name.split(".")
        file_name = file_name[0].upper()
    # get file values
    file_attributes = db.execute(
        "SELECT * FROM sequences WHERE file_id = ?", file_number)
    # split file attributes into different variables
    file_attributes = file_attributes[0]
    liau_index = file_attributes["liau_index"]
    liau_age = file_attributes["liau_age"]
    liau_grade = file_attributes["liau_grade"]
    flesch_kincaid_index = file_attributes["flesch_kincaid_index"]
    flesch_kincaid_grade = file_attributes["flesch_kincaid_grade"]
    gunning_fog_index = file_attributes["gunning_fog_index"]
    gunning_fog_grade = file_attributes["gunning_fog_grade"]
    automated_readability_index = file_attributes["automated_readability_index"]
    automated_readability_grade = file_attributes["automated_readability_grade"]
    words = file_attributes["words"]
    letters = file_attributes["letters"]
    sentences = file_attributes["sentences"]
    syllables = file_attributes["syllables"]
    complex_words = file_attributes["complex_words"]
    recommended_level = file_attributes["recommended_level"]
    return jsonify(render_template("historyImage.html", recommended_level=recommended_level, file_name=file_name, flesch_kincaid_index=flesch_kincaid_index, flesch_kincaid_grade=flesch_kincaid_grade, liau_index=liau_index, liau_age=liau_age, liau_grade=liau_grade, gunning_fog_index=gunning_fog_index, gunning_fog_grade=gunning_fog_grade, automated_readability_index=automated_readability_index, automated_readability_grade=automated_readability_grade, words=words, letters=letters, sentences=sentences, syllables=syllables, complex_words=complex_words,))


@ app.route("/account", methods=["GET", "POST"])
@ login_required
def account():
    user_id = session["user_id"]  # get user id
    # get user email + username + password (cannot be used since its hashed)
    user_attr = db.execute("SELECT * FROM clients WHERE id = ?", user_id)
    user_attr = user_attr[0]
    username = user_attr["username"]  # get user username
    password = "**********"  # password sample
    email = user_attr["email"]  # get user email
    return render_template("account.html", username=username, password=password, email=email)
