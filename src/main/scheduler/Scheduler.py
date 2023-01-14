import sys
import re
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None



#strong password
def strongPass(password):
    #At least 8 characters.
    def strongPass(password):
    #At least 8 characters.
        if len(password) < 8:
            return False
        #A mixture of both uppercase and lowercase letters.
        #A mixture of letters and numbers.
        #Inclusion of at least one special character, from “!”, “@”, “#”, “?”.
        spe_cha = ["!","@","#","?"]
        upper = False
        lower = False
        numbers = False
        special = False
        for i in password:
            if i.islower():
                lower = True
            if i.isupper():
                upper = True
            if i.isnumeric():
                numbers = True
            if i in spe_cha:
                special = True
        if upper and lower and numbers and special:
            return True
        
        return False

#create patients
def create_patient(tokens):
    # create_patient <username> <password>
    # tokens need to be exactly 3 to include all informantion
    if len(tokens)!=3:
        print("Please try again!")
        return
    
    username = tokens[1]
    password = tokens[2]
    #check is the username has already been taken
    if username_exists_patient(username):
        print("Username taken, try again")
        return
    
    
    salt = Util.generate_salt()
    hash = Util.generate_hash(password,salt)
        
    #create the patient
    try:
        patient = Patient(username, salt = salt, hash = hash)
        #save information to database
        patient.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create Faild!")
        return
        
        
#create caregiver
def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        caregiver.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


#check patient username
def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False

# check caregiver username
def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def login_patient(tokens):
    # login <username><password>
    #check 1: if someone's already logged-in, needs to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("Already logged-in!")
        return
    
    #check 2: the length for tokens need to be exactly 3 to include all info
    if len(tokens) != 3:
        print("Please try again!")
        return
    
    username = tokens[1]
    password = tokens[2]
    
    patient = None
    
    try:
        patient = Patient(username, password = password).get()
    except pymssql.Error:
        print("Error occurred when logging in")
    
    #check if the login was successful
    if patient is None:
        print("Password is wrong! Please try again!")
        return
    else:
        print("Patient logged in as: " + username)
        current_patient = patient
    
    
def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
        return
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    #search_caregiver_schedule <date>
    #check the length of tokens need to be exactly 3 to include all information
    if len(tokens)!=2:
        print("Please try again!")
        return
    # check someone have loged in whether caregiver or patient
    if current_caregiver is None and current_patient is None:
            print("Please Log in first!")
            return
    
    date  = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    
    #connecting server
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    #cargiver date and doses availabilties
    caregiver_data = "SELECT * FROM Availabilities WHERE Time = %s"
    dose_available = "SELECT * FROM Vaccines"
    
    #Output the username for the caregivers that are available for the date, along with the number of available doses left for each vaccine.
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(caregiver_data, d)
        for row in cursor:
            if row[1] is not None:
                print("Availabel Time:" + str(row[0]) +", Available Caregivers: " + str(row[1]))
            else:
                print("No Available Caregivers")
                
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error:
        print("Error occurred when getting details from Availabilities")
        cm.close_connection()
    cm.close_connection()
    #getting details from vaccines
    try:
        cursor.execute(dose_available)
        for row in cursor:
            print("Vaccine Name: " + str(row[0]) + ", Available Doses: " + str(row[1]))
    except pymssql.Error:
        print("Error occurred when getting details from Vaccines")
        cm.close_connection()
    cm.close_connection()


def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    
    
    #reserve <date> <vaccine>
    #check the length of tokens need to be exactly 3 to include all information
    if len(tokens) != 3:
        print("Please try agian!")
        return
    #check if the current logged-in user is a patient
    if current_patient is None:
        print("Please login as a Patient first!")
        return
    
    date = tokens[1]
    vaccine = tokens[2]
    
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    
    #connecting server
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    id = 1
    max_id = "Select max(id) From Appointments"
    
    
    
    #You will be randomly assigned a caregiver for the reservation on that date.
    #Output the assigned caregiver and the appointment ID for the reservation.
    assigned_caregiver = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY NEWID()"
    check_vaccine = "SELECT * FROM Vaccines WHERE Name = %s"
    
    try:
    
        #id
        cursor.execute(max_id)
        for row in cursor:
            if row[0] is not None:
                id = row[0]
    
        d = datetime.datetime(year, month, day)
        #check vaccines first
        cursor.execute(check_vaccine, vaccine)
        for row in cursor:
            #vname is none
            if row[0] is None:
                print("Select a available vaccine")
                return
            #dose number is 0
            if row[1] == 0:
                print("There is no vaccine available at this time")
                return
        #randomly assigned a caregiver
        cursor.execute(assigned_caregiver, d)
        for row in cursor:
            #caregiver is none
            if row[0] is None:
               print("No available caregiver, please select another time")
               return
            print("Assigned Caregiver: " + str(row[0]) + ", Appointment ID: " + str(id))
            #insert reservation into appointment table
            current_patient.upload_appointment(d,id,str(row[0]),vaccine)
            #delete from availabilities
            current_patient.delete_ava(d,str(row[0]))
        
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error:
        print("Error occurred when getting details from Vaccines")
        cm.close_connection()
    cm.close_connection()
    


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    if len(tokens) != 2:
        print("please try again")
        return
    cancel = "Delete From Appointments Where ID = %s"
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    id = tokens[1]
    try:
        cursor.execute(cancel, id)
        print("delete done")
        conn.commit()
    except pymssql.Error:
        print("Error occurred when deleting appointment")
        cm.close_connection()
    cm.close_connection()
    
    
def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = str(tokens[1])
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            vaccine.save_to_db()
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error:
            print("Error occurred when adding doses")

    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    #connecting server
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    
    #For caregivers, you should print the appointment ID, vaccine name, date, and patient name.
    caregiver_appointment = "SELECT ID,vname,Time,PUsername FROM Appointments WHERE CUsername = %s"
    #For patients, you should print the appointment ID, vaccine name, date, and caregiver name.
    patient_appointment = "SELECT ID, vname, Time, CUsername FROM Appointments WHERE PUsername = %s"
    # for caregiver
    if current_caregiver is not None:
        try:
            cursor.execute(caregiver_appointment, current_caregiver.get_username())
            for row in cursor:
                print("Appointment ID: " + str(row[0]) + ", Vaccine Name: " + str(row[1]) + ", Date: " + str(row[2]) + ", Patient Name: " + str(row[3]))
        except pymssql.Error:
            print("Error Occured when showing appointments")
            cm.close_connection()
    
    #for patient
    elif current_patient is not None:
        try:
            cursor.execute(patient_appointment, current_patient.get_username())
            for row in cursor:
                print("Appointment ID: " + str(row[0]) + ", Vaccine Name: " + str(row[1]) + ", Date: " + str(row[2]) + ", Caregiver Name: " + str(row[3]))
        except pymssql.Error:
            print("Error Occured when showing appointments")
            cm.close_connection()
        cm.close_connection()
    #on one loged in
    else:
        print("Please Login first!")
        return

# there is no need for tokens for log out
def logout(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver
    # check patient have loged-in first
    if current_patient is not None:
        #log out for patient
        current_patient = None
        print("Logout Successed!")
    # check caregiver have loged-in first
    elif current_caregiver is not None:
        #log out for caregiver
        current_caregiver = None
        print("Logout Successed!")
    # there is no one loged-in first
    else:
        print("Please Login First!")
        return



def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  #// TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  #// TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") #// TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") #// TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  #// TODO: implement show_appointments (Part 2)
        print("> logout") #// TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
