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

# Extra Bonus: add guidelines for strong password 
def valid_password(password):
    if len(password)<8:
        print('password should be at least 8 characters long.')
        return False
    if password.islower() or password.isupper():
        print('password should contain both upper and lower case character.')
        return False
    if not any(c in '!@#?' for c in password):
        print('password should contain at least one special character from !@#?.')
        return False
    return True


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]

    # bonus, check if password is strong enough
    if not valid_password(password):
        return

    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    
    # bonus, check if password is strong enough
    if not valid_password(password):
        return

    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    if len(tokens)!=2:
        print('invalid input')
        return 
    
    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    select_availabilities = "SELECT * FROM Availabilities WHERE time = %s ORDER BY Username"
    check_doses = 'SELECT * FROM Vaccines'
    try:
        print('============= Available Caregivers =============')

        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_availabilities, d)
        for row in cursor:
            print(row['Username'])
        
        print('============= Available Vaccines ===============')

        cursor.execute(check_doses)
        for row in cursor:
            print(row['Name'],' ',row['Doses'])

    except pymssql.Error as e:
        print("Error occurred when searching caregiver schedule")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching caregiver schedule")
        print("Error:", e)
    finally:
        cm.close_connection()
    return


def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    if current_patient is None:
        print('Please login as a patient!')
        return
    
    if len(tokens)!=3:
        print("Please try again, invalid input length")
        return

    _,date,vaccine = tokens
    patient = current_patient.get_username()

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    cm = ConnectionManager()
    conn = cm.create_connection()

    select_availabilities = "SELECT * FROM Availabilities WHERE time = %s ORDER BY Username"
    select_vaccine = "SELECT * FROM Vaccines WHERE Name = %s"
    
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_availabilities, d)
        appointment = [row for row in cursor]
        if len(appointment) == 0:
            print('No Caregiver is available!')
            return

        cursor.execute(select_vaccine, vaccine)
        vaccines = [row for row in cursor]
        if len(vaccines) == 0:
            print('Not enough available doses!')
            return
        if vaccines[0]['Doses'] == 0:
            print('Not enough available doses!')
            return
        
        number_of_vaccine = vaccines[0]['Doses']-1

        caregiver = appointment[0]['Username']
        counter = "SELECT * FROM Appointments"
        cursor.execute(counter)
        appointment_id = len([row for row in cursor])+1
        print('Appointment ID: {}, Caregiver username: {}'.format(appointment_id,caregiver))

        delete_availabilities = "DELETE FROM Availabilities WHERE time = %s AND Username = %s"
        cursor.execute(delete_availabilities,(d,caregiver))

        delete_vaccine = "DELETE FROM Vaccines WHERE Name = %s"
        cursor.execute(delete_vaccine, vaccine)
        update_vaccine = "INSERT INTO Vaccines VALUES (%s , %s)"
        cursor.execute(update_vaccine,(vaccine,number_of_vaccine))

        update_appointment = "INSERT INTO Appointments VALUES (%s , %s , %s , %s , %s)"
        cursor.execute(update_appointment,(appointment_id,d,caregiver,patient,vaccine))
        conn.commit()

        return
    
    except Exception as e:
        print("Please try again")
        print(e)
    finally:
        cm.close_connection()
    
    return
    


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
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


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

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        if current_patient is None and current_caregiver is None:
            print('Please login first!')
            return
        if current_patient is not None:
            patient = current_patient.get_username()
            get_appointment = "SELECT * FROM Appointments WHERE Patient = %s ORDER BY appointmentID"
            cursor.execute(get_appointment, patient)
            for row in cursor:
                print('{} {} {} {}'.format(row['appointmentID'],row['Vaccine'],row['Time'],row['Caregiver']))
        elif current_caregiver is not None:
            caregiver = current_caregiver.get_username()
            get_appointment = "SELECT * FROM Appointments WHERE Caregiver = %s ORDER BY appointmentID"
            cursor.execute(get_appointment, caregiver)
            for row in cursor:
                print('{} {} {} {}'.format(row['appointmentID'],row['Vaccine'],row['Time'],row['Patient']))
        return
    
    except Exception as e:
        print('Please try again')
        print(e)
        return

def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    try:
        if current_patient is None and current_caregiver is None:
            print('Please login first!')
            return 
        
        current_patient = None
        current_caregiver = None

        print('Successfully logged out!')
        
        return     

    except:
        print('Please try again!')
        return

def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break
        
        lower_response = response.lower()
        tokens = lower_response.split(" ")

        og_tokens = response.split(" ") # to keep the upper and lower case information

        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(og_tokens)
        elif operation == "create_caregiver":
            create_caregiver(og_tokens)
        elif operation == "login_patient":
            login_patient(og_tokens)
        elif operation == "login_caregiver":
            login_caregiver(og_tokens)
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
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


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
