import sqlite3
import pandas as pd
from pandas import DataFrame
from Student import Student


#error message strings
invalidEntryStringMessage = "Invalid entry. Please enter an alphabetical string."
invalidGPAMessage = "Invalid GPA. You must enter a numeric value between 0.00 and 4.00."
invalidSelectionErrorMessage = "Invalid selection. You must enter a numeric value between 1 and 6. Try again."
invalidEntry = "Invalid Entry. Try again."

### SQL STRINGS

#create table SQL Statements string
createStudentTableSQL = '''CREATE TABLE IF NOT EXISTS Students (
                        Id INTEGER primary key,
                        FirstName VARCHAR(25),
                        LastName VARCHAR(25))'''
                        
                        
createStudentMajorTableSQL = '''CREATE TABLE IF NOT EXISTS StudentMajor (
                            StudentID INT,
                            MajorID INT,
                            foreign key (StudentID) references Students(Id),
                            foreign key (MajorID) references Majors(Id),
                            UNIQUE (StudentID, MajorID) )'''
                            
                            
createStudentGPATableSQL = '''CREATE TABLE IF NOT EXISTS StudentGPA (
                            StudentID INT,
                            GPA NUMERIC,
                            foreign key (StudentID) references Students(Id),
                            UNIQUE (StudentID) )'''


createStudentAdvisorTableSQL = '''CREATE TABLE IF NOT EXISTS StudentAdvisor (
                                StudentID INT,
                                FacultyID INT,
                                foreign key (StudentID) references Students(Id),
                                foreign key (FacultyID) references FacultyAdvisors(Id),
                                UNIQUE (StudentID, FacultyID) )'''


createStudentAddressTableSQL = '''CREATE TABLE IF NOT EXISTS StudentAddress (
                                StudentID INT,
                                Address VARCHAR,
                                foreign key (StudentID) references Students(Id),
                                UNIQUE (StudentID, Address) )'''
                 
                 
createTableMajorsSQL = '''CREATE TABLE IF NOT EXISTS Majors (
                        Id INTEGER PRIMARY KEY,
                        Name VARCHAR(10) )'''
                        
                        
createTableFacultyAdvisorsSQL = '''CREATE TABLE IF NOT EXISTS FacultyAdvisors (
                                Id INTEGER PRIMARY KEY,
                                Name VARCHAR(25) )'''
                                
tablesSQLArray = [createStudentTableSQL, createStudentMajorTableSQL, createStudentGPATableSQL, createStudentAdvisorTableSQL, createStudentAddressTableSQL, createTableMajorsSQL, createTableFacultyAdvisorsSQL]

#select statement to join all the tables
displayAll = "SELECT Students.Id, Students.FirstName, Students.LastName, StudentAddress.Address, Majors.Name AS 'Major', FacultyAdvisors.Name AS 'FacultyAdvisor', StudentGPA.GPA FROM Students "\
                 "JOIN StudentMajor ON Students.Id = StudentMajor.StudentID "\
                 "JOIN Majors ON Majors.Id = StudentMajor.MajorID "\
                 "JOIN StudentAdvisor ON Students.Id = StudentAdvisor.StudentID "\
                 "JOIN FacultyAdvisors ON StudentAdvisor.FacultyID = FacultyAdvisors.Id "\
                 "JOIN StudentAddress ON Students.Id = StudentAddress.StudentID "\
                 "JOIN StudentGPA ON StudentGPA.StudentID = Students.Id"
                 



def createAllTables(tablesArray):
    for sql in tablesArray:
        c.execute(sql)
        conn.commit()
    
####functions for checking input

#function to get user input and validate it
#takes in a string that will prompt the user of what to input, an error message for if the input is invalid, and the type that the input should be
#if it is of valid type, return the user input, if not loop around and prompt the user to enter it again
def checkUserInput(userPrompt, errorMessage, typeCheck, inputLength):
    while True:
        userInput = input(userPrompt)
        if typeCheck == str:

            if validateString(userInput, errorMessage, inputLength) == True:
               return userInput
               break
        elif typeCheck == float:
            if validateNumeric(userInput, 4, errorMessage) == True:
                return userInput
                break


# function checks if a string is a word (no numbers or characters)
# it takes in the user input and an error message
# if it is valid, return true, if not, return false
def validateString(userInput, errorMessage, inputLength):
    if checkEmptyInput(userInput) == True:
        if userInput.isalpha():
            if len(userInput) > inputLength:
                print("Please limit your input to", inputLength, " characters.")
                return False
            return True
        else:
            print(errorMessage)
            return False
    return False

#checks user input does not equal empty string
def checkEmptyInput(userInput):
    if userInput == '':
        print("No input. Try again.")
        return False
    else:
        return True

# function checks if a input is a numeric value
# it takes in the user input, the maximum value of the number allowed, and an error message
# if it is valid, return true, if not, print error message and return false
def validateNumeric(userInput, maxValue, errorMessage):
    if checkEmptyInput(userInput) == True:
        try:
            input = float(userInput)
            if input < 0 or input > maxValue:
                print(errorMessage)
            else:
                return True

        except:
            print(errorMessage)
        return False
    return False

####functions to work with db (selects, inserts, updates, deletes)

#function to check if a database is empty
# takes in the table name as a string and
# returns true if db is empty, false if not empty
def isDBEmpty(table):
    c.execute('SELECT COUNT(*) FROM {}'.format(table))
    entries = c.fetchone()
    if entries[0] == 0:
        print("\nThe {} database is empty.".format(table))
        return True
    return False

#function to check if an id exists in a db
# takes in the table name as a string and the id
# returns true if id exists, false if doesnt exist
def doesIDExist(id, db):
    try:
        int(id)
        c.execute("SELECT Id FROM {} WHERE Id = ?;".format(db), (id,))
        data = c.fetchone()
        if data is None:
            print("This ID does not exist in the {} database. Try again.".format(db))
            return False
        else:
            return True
    except:
        print("That is not a valid ID. Try again entering one of the listed integers.")
        return False

#function to see how many values will be queried by and returns the count
def checkForValues(values):
    count = 0
    for x in range(len(values)):
        if values[x] != '':
            count += 1
    return count

#function adds new student and gets the id to add the student and it's values to each table
def addNewStudent(student) :
    c.execute("INSERT INTO Students('FirstName', 'LastName')" "VALUES (?,?)", (student.firstName, student.lastName,))
    studentId = c.lastrowid
    c.execute("INSERT INTO StudentAdvisor('StudentID','FacultyID')" "VALUES (?,?)", (studentId, student.facultyAdvisor,))
    # puts new student into the db
    c.execute("INSERT INTO StudentGPA('StudentID', 'GPA')"
          "VALUES (?,?)", (studentId, student.gpa,))
    c.execute("INSERT INTO StudentMajor('StudentID', 'MajorID')" "VALUES (?,?)", (studentId, student.major,))
    c.execute("INSERT INTO StudentAddress('StudentID', 'Address')" "VALUES (?,?)", (studentId, student.address,))
    conn.commit()
    return studentId


#function to add a new major to major table then returns the id of the new major
def addNewMajor():
    newMajor = checkUserInput("Enter the name of the new major: ", invalidEntryStringMessage, str, 10)
    c.execute("INSERT INTO Majors('Name')" "VALUES (?)", (newMajor,))
    conn.commit()
    return c.lastrowid

#function to add a new advisor to advisor table then returns the id of new advisor
def addNewAdvisor():
    newAdvisor =checkUserInput("Enter the name of the new advisor: ", invalidEntryStringMessage, str, 25)
    c.execute("INSERT INTO FacultyAdvisors('Name')" "VALUES (?)", (newAdvisor,))
    conn.commit()
    return c.lastrowid

#the following functions displays tables using simple select statments
def displyAdvisors():
    df = pd.read_sql_query("SELECT * FROM FacultyAdvisors;", conn)
    print(df)

def displayMajors():
    df = pd.read_sql_query("SELECT * FROM Majors;", conn)
    print(df)

def displayStudents():
    df = pd.read_sql_query("SELECT * FROM Students;", conn)
    print(df)

#the following functions updates tables with simple select statments usind the value to be updated and the student id
def updateStuMajor(major, id):
    c.execute('UPDATE StudentMajor SET MajorID = ? WHERE StudentId = ?', (major, id,))

def updateStuAdvisors(advisor, id):
    c.execute('UPDATE StudentAdvisor SET FacultyID = ? WHERE StudentId = ?', (advisor, id,))


def updateStuAddress(address, id):
    c.execute('UPDATE StudentAddress SET Address = ? WHERE StudentId = ?', (address, id,))

#takes in a student id and deletes it from student table as well as any references in other tables
def deleteStudent(id):
    c.execute("DELETE FROM Students WHERE Id = ?", (id,))
    c.execute("DELETE FROM StudentMajor WHERE StudentID = ?", (id,))
    c.execute("DELETE FROM StudentGPA WHERE StudentID = ?", (id,))
    c.execute("DELETE FROM StudentAdvisor WHERE StudentID = ?", (id,))
    c.execute("DELETE FROM StudentAddress WHERE StudentID = ?", (id,))
    conn.commit()

#display all students
def displayAllStudentInfo():
    df = pd.read_sql_query(
        displayAll, conn)
    print(df)

#display student with id
def displayStudentInfoById(id):
    df = pd.read_sql_query(
         "{} WHERE Students.Id = ?;".format(displayAll), conn, params= (id,))
    print(df)

#function to query by major and/or advisor and/or gpa
#use checkForValues function to see how many values user is searching by
#use this info to perform proper query
def queryAndDisplayAllStudentInfo(major, advisor, gpa):
    #arrays to be used and indexed in queries
    values = [major, advisor, gpa]
    name = ['MajorID', 'FacultyID', 'GPA']

    #initializinng result to an empty df
    result = pd.DataFrame()

    #if user searches by all 3 values, construct query and set result
    if checkForValues(values) == 3:
        result = pd.read_sql_query(
            "{} WHERE {} = ? AND {} = ? AND {} = ?;".format(displayAll, name[0], name[1], name[2]), conn,
            params=(values[0], values[1], values[2]), )

    #if user searches by 2 values
    #iterate through value array to find the two values that are being searched for and construct search and set result
    elif checkForValues(values) == 2:
        for x in range(len(values)):
            if (values[x % len(values)] != '') & (values[(x + 1) % len(values)] != ''):
                result = pd.read_sql_query("{} WHERE {} = ? AND {} = ?;"
                                           .format(displayAll, name[x], name[(x + 1) % len(values)]), conn,
                                           params=(float(values[x]), values[(x + 1) % len(values)],))
                break

    #if user only searches by one value
    #find the value being searched on and construct query and set result
    elif checkForValues(values) == 1:
        for x in range(len(values)):
            if values[x] != '':
                result = pd.read_sql_query("{} WHERE {} = ?;".format(displayAll, name[x]), conn,
                                           params=(float(values[x]),))
                break

    #if result set is empty
    if result.empty:
        #and if user did not do any searches
        if checkForValues(values) == 0:
            print("\nYou did not search by anything.")
        #if user searched but no  matching results
        else:
            print("Your search did not match any Student records")
    #if result set is not empty, print out dataframe results
    else:
        print(result)


#### START OF MAIN PART OF PROGRAM

while True :

    #connects to db
    conn = sqlite3.connect('StudentDataBase.db')
    c = conn.cursor()
    createAllTables(tablesSQLArray)

    #initialized to empty string so that when it loops around, input value is reset
    promptSelection = ""
    userPrompt = input("\nSelect from the following options: "
                       "\n 1. Display all Students and their attributes\n "
                       "2. Create a new student. \n "
                       "3. Update a student.\n "
                       "4. Delete a student. \n "
                       "5. Search students. \n "
                       "6. Add new advisor. \n "
                       "7. Add new major. \n "
                       "8. Exit program.\n")

    if validateNumeric(userPrompt, 8, invalidSelectionErrorMessage):
        try:
            promptSelection = int(userPrompt)
        except:
            print(invalidSelectionErrorMessage)

    #if user selects 1, display all students by joining tables together
    if promptSelection == 1:
        if isDBEmpty('Students') == False:
            print("\nDisplaying all students...\n")
            displayAllStudentInfo()

    #if user selects 2, prompt user to enter all attributes for new student,
    #and insert them into the Student db and all corresponding dbs
    #checks for valid input each time user gives input
    elif promptSelection == 2:

        print("\nCreating a new student...\nPlease enter all required fields.\n")

        #get first name input
        stuFirstName = checkUserInput("First Name: ", invalidEntryStringMessage, str, 25)

        #get last name input
        stuLastName = checkUserInput("Last Name: ", invalidEntryStringMessage, str, 25)

        #get gpa input then formats float to two decimal points
        stuGPA = checkUserInput("GPA: ", invalidGPAMessage, float, 0)
        stuGPANumeric = '%0.2f' % float(stuGPA)

        #get major input
        #first checks if major db is empty
        # then user has option to select an existing major or create a new one
        if isDBEmpty('Majors') == True :
            stuMajor = addNewMajor()
        else:
            while True:
                print("Choose from the list of Majors (Enter the Major ID) or press ENTER to add a new Major\n")
                displayMajors()
                stuMajor = input()

                if stuMajor == '':
                    stuMajor = addNewMajor()
                    break
                elif doesIDExist(stuMajor, 'Majors') == True :
                    break

        # get advisor input
        # first checks if advisor db is empty
        # then user has option to select an existing advisor or create a new one
        if isDBEmpty('FacultyAdvisors') == True :
            stuFacultyAdvisor = addNewAdvisor()
        else:
            while True:
                print("Choose from the list of Advisors (Enter faculty ID) or press ENTER to add a new Faculty Advisor\n")
                displyAdvisors()
                stuFacultyAdvisor = input()

                if stuFacultyAdvisor == '':
                    stuFacultyAdvisor = addNewAdvisor()
                    break
                elif doesIDExist(stuFacultyAdvisor, 'FacultyAdvisors') == True:
                    break

        #get address input
        while True:
            stuAddress = input("Enter the student Address: ")
            if checkEmptyInput(stuAddress) == True:
               break

        #sets newstudent
        newStudent = Student(stuFirstName, stuLastName, stuGPANumeric, stuMajor, stuFacultyAdvisor, stuAddress,)

        #adds new students to db using newStudent
        studentId = addNewStudent(newStudent)

        #prints out newly entered student
        displayStudentInfoById(studentId)

    #if user selects 3, ask user which student they would like to update
    #check student exists in db, if it does: allow user to update major and/or advisor and/or address,
    elif promptSelection == 3:
        updateStudent = Student

        if isDBEmpty('Students') == False:
            while True:
                print("\nEnter the ID of the student you would like to update: ")
                displayStudents()
                updateID = input()

                if doesIDExist(updateID, 'Students'):
                    #after prompted to enter new major, if the user presses 'enter', skip and move on, do not update this
                    #if they entered a value, update the student with new value
                    while True:
                        updateMajor = input("Would you like to update the student's Major? Y/N ").upper()
                        if updateMajor == 'Y':
                            print("Select from the list of majors or press ENTER to add a new major.")
                            displayMajors()
                            updateMajor = input()

                            if updateMajor == '':
                                addNewMajor()
                                updateMajor = c.lastrowid
                                updateStuMajor(updateMajor, updateID)
                                break

                            elif doesIDExist(updateMajor, 'Majors') == True:
                                updateStuMajor(updateMajor, updateID)
                                break

                        elif updateMajor == 'N':
                            break
                        else:
                            print(invalidEntry)
                            continue

                    #after prompted to enter new advisor, if the user presses 'enter', skip and move on, do not update this
                    #if they entered a value, update the student with new value
                    while True:
                        updateAdvisor = input("Would you like to update the student's Advisor? Y/N ").upper()
                        if updateAdvisor == 'Y':
                            print("Select from the list of advisors or press ENTER to add a new advisor.")
                            displyAdvisors()
                            updateAdvisor = input()

                            if updateAdvisor == '':
                                addNewAdvisor()
                                updateAdvisor = c.lastrowid
                                updateStuAdvisors(updateAdvisor, updateID)
                                break

                            elif doesIDExist(updateAdvisor, 'FacultyAdvisors') == True :
                                updateStuAdvisors(updateAdvisor, updateID)
                                break

                        elif updateAdvisor == 'N' :
                            break
                        else:
                            print(invalidEntry)
                            continue

                    while True:
                        updateAddress = input("Would you like to update the student's address? Y/N ").upper()

                        if updateAddress == 'Y':
                            updateAddress = input("Enter the new address: ")
                            updateStuAddress(updateAddress, updateID)
                            break

                        elif updateAddress == 'N':
                            break

                        else:
                            print(invalidEntry)
                            continue

                    conn.commit()

                    displayStudentInfoById(updateID)

                    break

                else:
                    continue

    #deletes student from the database based on users selection
    elif promptSelection == 4:
        if isDBEmpty('Students') == False:
            print("Enter the id of the student you would like to delete: ")
            displayStudents()
            idToDelete = input()
            deleteStudent(idToDelete)

    #prompts/allows user to search by major, advisor, and/or gpa of student
    #to skip one of the search attributes, press enter
    #pass the user input into queryAndDisplayAllStudentInfo() to get the results of query
    elif promptSelection == 5:
        if isDBEmpty('Students')== False:
            print('You can search for students by Major, GPA, and Advisor. If you do not want to search by one of these, press "Enter" to skip.')

            #prompts user for input
            print("Select from list of majors to search by or press 'ENTER' to skip: ")
            displayMajors()
            stuMajor = input()

            print("Select from the list of faculty advisors to search by or press 'ENTER' to skip: ")
            displyAdvisors()
            stuFacultyAdvisor = input()

            stuGPA = input("Search for GPA or press ENTER to skip: ")

            queryAndDisplayAllStudentInfo(stuMajor, stuFacultyAdvisor, stuGPA)

    #allows user to add new advisor
    elif promptSelection == 6:
        addNewAdvisor()

    #allows user to add new major
    elif promptSelection == 7:
        addNewMajor()

    # exits program
    elif promptSelection == 8:
        print("Goodbye")
        break

# close connection
conn.close()

