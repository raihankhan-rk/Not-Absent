from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore
from functionHandler import genKey, genCode
from twilio.rest import Client
from dotenv import load_dotenv
import os


app = Flask(__name__)
load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)


cred = credentials.Certificate('creds.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
collection = db.collection('attendance')


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/teacher/dashboard')
def dashboard():
    data = []
    studentData = db.collection('teacher').get()
    for item in studentData:
        data.append([item.to_dict()])
    return render_template('teacherDashboard.html', students=data)

@app.route('/teacher/add-student/submit', methods=['POST', 'GET'])
def addStudent_submit():
    if request.method == 'POST':
        enrolment_no = request.form['enrolment-no']
        name = request.form['name']
        stream = request.form['stream']
        password = request.form['password']
        phone = request.form['phone-no']
        #send the password to the phone no.
        collection.document(enrolment_no).set({'password': password, 'attendance_code': "", 'link_key': "", 'phone': f'+91{phone}'})
        db.collection('teacher').document(enrolment_no).set({'enr': enrolment_no, 'name': name, 'stream': stream, 'status': False, 'phone': f'+91{phone}'})
        # message = client.messages.create(
        #     body=f"You have been added to a classroom by your teacher. Your Enrolment No. is {enrolment_no} and your Password is {password}. You can give your attendance here at this link - ",
        #     from_=os.getenv('MY_TWILIO_PHONE_NO'),
        #     to=f"+91{phone}"
        # )
        # print(message.sid)
        return redirect('/teacher/dashboard')
    else:
        return redirect('/teacher/add-student')

@app.route('/teacher/add-student')
def addStudent():
    return render_template('addStudent.html')

@app.route('/student/attendance')
def authenticateStudent():
    return render_template('authenticate.html')

@app.route('/student/attendance/submit', methods=['GET', 'POST'])
def authenticate_submit():
    if request.method == 'POST':
        enrolment_no = request.form['enrolment-no']
        password = request.form['password']
        if collection.document(enrolment_no).get().to_dict() is not None:
            res = collection.document(enrolment_no).get().to_dict()
            if res['password'] == password:
                key = genKey()
                collection.document(enrolment_no).update({'link_key': key})
                return redirect(f'/student/attendance/{enrolment_no}/{key}')
            else:
                return "Incorrect Password"
        else:
            return "No such student found in Database!"
    else:
        return redirect('/attendance')

@app.route('/student/attendance/<string:enr>/<string:key>')
def specificStudentAttendance(enr, key):
    if (collection.document(enr).get().to_dict())['link_key'] == key:
        code = genCode()
        # message = client.messages.create(
        #     body=f"Your Attendance Code for this class is {code}",
        #     from_=os.getenv('MY_TWILIO_PHONE_NO'),
        #     to=collection.document(enr).get().to_dict()['phone']
        # )
        # print(message.sid)
        print(code)
        collection.document(enr).update({'attendance_code': code})
        return render_template("attendanceCode.html", enr=enr, key=key)
    else:
        return "<h1>Unauthorized<h1>"

@app.route('/student/attendance/<string:enr>/<string:key>/v', methods=['GET', 'POST'])
def verifyAttendanceCode(enr, key):
    if request.method == 'POST':
        if (collection.document(enr).get().to_dict())['attendance_code'] == request.form['attendance_code']:
            db.collection('teacher').document(enr).update({'status': True})
            return "<h1>Attendance Verified!</h1><p>You have been marked present.</p>"
        else:
            db.collection('teacher').document(enr).update({'status': False})
            return "<h1>Attendance could not be verified!</h1><p>You have been marked absent.</p>"
    else:
        return redirect(f'/attendance/{enr}/{key}')


if __name__ == '__main__':
    app.run(debug=True)