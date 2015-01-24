#########################################################################
# Program Name: Robot Registrator 3000
# Author:       Mark Moussa
# Purpose:      Automatically searches and registers classes for you.
#########################################################################

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from tkinter import *
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from lxml import html

"""MAKE QUIT BUTTON ON TIMER WINDOW DESTROY PROGRAM. INCLUDE CENTER PAUSE BUTTON THAT DOES WHAT QUIT DOES NOW"""

first_time = True

#setting the scheduler in order to use later in script
ap_scheduler = BackgroundScheduler()
executors = {
    'default': ProcessPoolExecutor()
}
ap_scheduler.configure(executors=executors)
ap_scheduler.daemonic = True
ap_scheduler.start()


#variable made in order to pass things by raising exception
skip_rest_of_function = False


def timer(username, password, term, crn1):
    ap_scheduler.add_job(submit_crn, 'interval', seconds=timer_as_integer, args=(username, password, term, crn1))


def submit_crn(username, password, term, crn1):
    """Happens when user presses RUN in order to register for CRN"""

    #Edit according to specific path on person's computer
    driver = webdriver.PhantomJS()
    driver.get("http://oasis.usf.edu")
    #Click login button on OASIS
    wait = WebDriverWait(driver, time.time, 5)
    login_button = driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[4]/a")
    login_button.click()
    wait
    username_area = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/form/input[1]")
    username_area.send_keys(username)
    password_area = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/form/input[2]")
    password_area.send_keys(password)
    password_area.submit()
    #wait for code to process to make sure page is loaded
    wait
    #clicks on Student
    try:
        student = driver.find_element_by_xpath("/html/body/div[3]/table[1]/tbody/tr[2]/td[2]/a")
        student.click()
    except NoSuchElementException:
        AutomaticClassRegistration.wrong_credentials()
        driver.close()
    #clicks on Registration
    registration = driver.find_element_by_link_text("Registration")
    registration.click()
    wait
    #clicks on Register, Add or Drop Classes
    register_class = driver.find_element_by_link_text("Register, Add or Drop Classes")
    register_class.click()
    wait
    #checks if it asks for which term. if it does, selects term, if not, passes
    try:
        (EC.presence_of_element_located("/html/body/div[3]/form/table/tbody/tr[1]/td[2]/select"))
        if term == ("SPRING"):
            term_drop = Select(driver.find_element_by_xpath("/html/body/div[3]/form/table/tbody/tr[1]/td[2]/select"))
            term_drop.select_by_visible_text("Spring 2015")
            submit_term_drop = driver.find_element_by_xpath("/html/body/div[3]/form/input")
            submit_term_drop.click()
        elif term == ("SUMMER"):
            term_drop = Select(driver.find_element_by_xpath("/html/body/div[3]/form/table/tbody/tr[1]/td[2]/select"))
            term_drop.select_by_visible_text("Summer 2015")
            submit_term_drop = driver.find_element_by_xpath("/html/body/div[3]/form/input")
            submit_term_drop.click()
        elif term == ("FALL"):
            term_drop = Select(driver.find_element_by_xpath("/html/body/div[3]/form/table/tbody/tr[1]/td[2]/select"))
            term_drop.select_by_visible_text("Fall 2015")
            submit_term_drop = driver.find_element_by_xpath("/html/body/div[3]/form/input")
            submit_term_drop.click()
    except:
        pass
    wait
    try:
        crn1_input = driver.find_element_by_id("crn_id1")
    except NoSuchElementException:
        global skip_rest_of_function
        skip_rest_of_function = True
        AutomaticClassRegistration.cannot_send_registration_field()
    #if registration is closed, it passes rest of function
    if skip_rest_of_function:
        pass
    else:
        crn1_input.send_keys(crn1)
        #add entry fields for other CRN slots, in if/else statements for blank.
        driver.find_element_by_xpath("/html/body/div[3]/form/input[19]").click()
        wait
        current_url = driver.page_source
        try:
            #searches for the Registration Error field
            driver.find_element_by_xpath("/html/body/div[3]/form/table[3]/tbody/tr/td[2]/span")
            tree = html.fromstring(current_url)
            error = tree.xpath("/html/body/div[3]/form/table[4]/tbody/tr[2]/td[1]//text()")
            #takes away { and } in the error message to look better in GUI
            global new_error
            new_error = []
            for x in error:
                if (x == "{") or (x == "}"):
                    pass
                else:
                    new_error.append(x)
            new_error = ''.join(new_error)
            print(new_error)
        except NoSuchElementException:
            AutomaticClassRegistration.registration_successful()
    driver.close()


def timer_terminate_from_button():
    """IN CASE USER WANTS TO QUIT TIMER PROCESS FROM POPUP WINDOW"""
    print("timer_terminate_from_button()")
    ap_scheduler.remove_all_jobs()


def on_class_schedule_search_submission(semester, campus, subject, number):

    campus_xpath = "/html/body/form/table/tbody/tr[4]/td[2]/select"
    subject_xpath = "/html/body/form/table/tbody/tr[9]/td[2]/select"
    number_xpath = "/html/body/form/table/tbody/tr[10]/td[2]/div[1]/input"
    search_button_xpath = "/html/body/form/table/tbody/tr[20]/td/input[1]"
    #when problem with PhantomJS and Chromedriver are solved, add if/else statement setting
    #driver to something else in case initial browser is not installed in system
    #(if user has Firefox then webdriver.Firefox, if not then webdriver.Chrome, etc)
    driver = webdriver.Firefox()
    driver.get('http://www.registrar.usf.edu/ssearch/search.php')
    wait = WebDriverWait(driver, 20)
    WebDriverWait(driver, 20)
    #Sets variables, asks for which campus, if answer matches any one, then it selects proper option
    select_campus_choice = Select(driver.find_element_by_xpath(campus_xpath))
    #wait.until statements wait for computer to select element, in case there is an obstacle/slowdown in the way
    wait.until(EC.presence_of_element_located((By.XPATH, campus_xpath)))

    if campus.upper() == ("TAMPA"):
        select_campus_choice.select_by_value("1")
    elif campus.upper() == ("SARASOTA"):
        select_campus_choice.select_by_value("2")
    elif campus.upper() == ("ST. PETERSBURG"):
        select_campus_choice.select_by_value("3")
    elif campus.upper() == ("LAKELAND"):
        select_campus_choice.select_by_value("4")
    elif campus.upper() == ("OFF CAMPUS"):
        select_campus_choice.select_by_value("5")
    else:
        print("Oops! Looks like your choice wasn't valid. Try typing it in a different way, preferably how the \
options asked you to exactly.")

    wait.until(EC.presence_of_element_located((By.XPATH, subject_xpath)))
    select_subject_choice = Select(driver.find_element_by_xpath(subject_xpath))
    try:
        select_subject_choice.select_by_value(subject.upper())
    except:
        print("Oops! Looks like you didn't input the right thing. Remember the subject should be the letters, \
not the actual subject name, e.g. Chemistry = CHM")

    wait.until(EC.presence_of_element_located((By.XPATH, number_xpath)))
    select_number_choice = (driver.find_element_by_xpath(number_xpath))
    select_number_choice.send_keys(number)
    #When finished with all search queries, the next two lines find search button and click it
    select_submit_button = (driver.find_element_by_xpath(search_button_xpath))
    select_submit_button.click()


######################################################################################################################
# GUI CLASS STARTS HERE
######################################################################################################################

class AutomaticClassRegistration():

    #@property functions define the information the user gives us in the GUI so we can relay it to functions outside
    @property
    def username(self):
        return self.username_field.get()

    @property
    def password(self):
        return self.password_field.get()

    @property
    def term(self):
        return self.term_field.get()

    @property
    def crn1(self):
        return self.crn1_field.get()

    @property
    def semester(self):
        return self.semester_choice.get()

    @property
    def campus(self):
        return self.campus_choice.get()

    @property
    def subject(self):
        return self.subject_choice.get()

    @property
    def number(self):
        return self.number_choice.get()

    def __init__(self):
        self.root = Tk()
        self.root.title("automatic_class_registration")
        self.timer_terminate = False
        #create the buttons and message label for first tk instance
        message_frame = Frame(self.root, width=3)
        message = Message(message_frame, text="Hello! This is an automatic registration program. If you already know the \
CRN, just press the button to the left that says CRN. If you still don't know what class you need, go ahead and press \
the RUN button, and it will search the field for you. You can then select which classes you want to have automated \
registration.")
        crn_button_frame = Frame(self.root, width=1)
        crn_button = Button(crn_button_frame, text="CRN", command=self.show_credentials_frame_crn)
        schedule_search_frame = Frame(self.root, width=1)
        schedule_search = Button(self.root, text="RUN", command=self.create_class_search_instance)
        message_frame.pack()
        message.pack()
        crn_button_frame.pack(side=LEFT)
        crn_button.pack(side=LEFT)
        schedule_search_frame.pack(side=RIGHT)
        schedule_search.pack(side=RIGHT)
        self.root.mainloop()

    def create_class_search_instance(self):

        """This is the search criteria entry for searching classes"""
        global entry_fields
        entry_fields = Tk()
        entry_fields.title("Search Criteria")

        #create entry fields for class search
        questions_frame = Frame(entry_fields)
        semester_label = Label(questions_frame, text="Which semester is this for?")
        self.semester_choice = Entry(questions_frame)
        campus_label = Label(questions_frame, text="Which campus is this for? ")
        self.campus_choice = Entry(questions_frame)
        subject_choice_label = Label(questions_frame, text="Which subject? Input the letters ONLY. eg. Chemistry = CHM")
        self.subject_choice = Entry(questions_frame)
        number_choice_label = Label(questions_frame, text="What is the number for the class?  ")
        self.number_choice = Entry(questions_frame)
        back_button_frame = Frame(entry_fields)
        back = Button(back_button_frame, text="BACK", command=self.back_to_beginning_frame_from_entry_fields)
        run_button_frame = Frame(entry_fields)
        run = Button(run_button_frame, text="RUN", command=self.grab_class_search_credentials)
        questions_frame.pack()
        semester_label.pack(fill=BOTH, expand=1)
        self.semester_choice.pack(fill=BOTH, expand=1)
        campus_label.pack(fill=BOTH, expand=1)
        self.campus_choice.pack(fill=BOTH, expand=1)
        subject_choice_label.pack(fill=BOTH, expand=1)
        self.subject_choice.pack(fill=BOTH, expand=1)
        number_choice_label.pack(fill=BOTH, expand=1)
        self.number_choice.pack(fill=BOTH, expand=1)
        back_button_frame.pack(side=LEFT)
        back.pack(side=LEFT)
        run_button_frame.pack(side=RIGHT)
        run.pack(side=RIGHT)
        #adding time and other options later
        self.root.destroy()

    def grab_class_search_credentials(self):
        on_class_schedule_search_submission(self.semester, self.campus, self.subject, self.number)

    def show_credentials_frame_crn(self):

        """Entry for if you already know the CRN number"""
        self.root.destroy()
        self.crn_instance = Tk()
        self.crn_instance.title("CRN Credential Information")
        #Put message instructing people what to do
        message_frame = Frame(self.crn_instance)
        message = Message(message_frame, text="Enter your USF OASIS credentials, (username, password), and the \
                                               CRN(s) of the class you would like to register for. Don't worry, we \
                                               don't save any of this data!")
        questions_frame = Frame(self.crn_instance)
        term_label = Label(questions_frame, text="What semester are you trying to register for? (Options are Spring, \
Fall, or Summer)")
        self.term_field = Entry(questions_frame)
        username_label = Label(questions_frame, text="Please enter your OASIS username:  ")
        self.username_field = Entry(questions_frame)
        password_label = Label(questions_frame, text="Please enter your OASIS password:  ")
        self.password_field = Entry(questions_frame, show="*")
        crn_label = Label(questions_frame, text="Please enter the CRN number for your class:  ")
        self.crn1_field = Entry(questions_frame)
        run_button_frame = Frame(self.crn_instance)
        run_crn = Button(run_button_frame, text="RUN", command=self.grab_crn_credentials)
        back_button_frame = Frame(self.crn_instance)
        back_button = Button(back_button_frame, text="BACK", command=self.back_to_beginning_frame_from_crn_field)
        message_frame.pack(side=TOP)
        message.pack(side=TOP)
        questions_frame.pack()
        term_label.pack(fill=BOTH, expand=1)
        self.term_field.pack(fill=BOTH, expand=1)
        username_label.pack(fill=BOTH, expand=1)
        self.username_field.pack(fill=BOTH, expand=1)
        password_label.pack(fill=BOTH, expand=1)
        self.password_field.pack(fill=BOTH, expand=1)
        crn_label.pack(fill=BOTH, expand=1)
        self.crn1_field.pack(fill=BOTH, expand=1)
        back_button_frame.pack(side=LEFT)
        back_button.pack(side=LEFT)
        run_button_frame.pack(side=RIGHT)
        run_crn.pack(side=RIGHT)

    def grab_crn_credentials(self):

        """Takes the information from the class registration page and passes them as args to submit_crn"""
        submit_crn(self.username, self.password, self.term, self.crn1)
        if first_time:
            self.registration_failure()
        elif not first_time:
            pass
        global first_time
        first_time = False

    @staticmethod
    def wrong_credentials():
        wrong_credentials = Tk()
        wrong_credentials.title("Error!")
        wrong_credentials_message = Message(wrong_credentials, text="Error! You seem to have entered the wrong \
username or password. Please check again. If that's not what's wrong, please contact the developer.")
        wrong_credentials_exit_button = Button(wrong_credentials, text="Try Again", command=wrong_credentials.destroy)
        wrong_credentials_message.pack(anchor=CENTER, fill=BOTH, expand=1)
        wrong_credentials_exit_button.pack(anchor=NE)

    @staticmethod
    def registration_successful(self):

        """Screen that pops up if registration for classes returned no error"""
        success_instance = Tk()
        success_instance.title("Registration Successful!")
        message = Message(success_instance, text="Congratulations! You have officially registered for the class you \
wanted.")
        close_button = Button(success_instance, text="Close", command=self.root.destroy)
        message.pack(fill=BOTH, expand=1)
        close_button.pack(anchor=SE)

    def registration_failure(self):
        """Screen that pops up if registration did return an error"""

        global failure_instance
        failure_instance = Tk()
        failure_instance.title("Error Returned!")
        message = Message(failure_instance, text="Apparently there was an error in registering your class.", aspect=400)
        error_message = Message(failure_instance, text=new_error, aspect=400)
        timer_label = Label(failure_instance, text="In how many minutes would you like to try again? (2 to 10)")
        global timer_setting
        timer_setting = Spinbox(failure_instance, from_=0, to=10)
        execute_timer_button = Button(failure_instance, text="CONTINUE", command=self.timer_tk)
        message.pack(fill=BOTH, expand=1)
        error_message.pack(anchor=CENTER)
        timer_label.pack()
        timer_setting.pack()
        execute_timer_button.pack(anchor=SE)

    @staticmethod
    def cannot_send_registration_field():

        """If registration is closed, it will throw an exception. This GUI instance catches and reports this"""
        cannot_register_class = Tk()
        cannot_register_class.title("Registration Is Closed")
        message = Message(cannot_register_class, text="It looks like the registration field for you is closed. Maybe registration \
                                         has passed? Try registering on your own and then come back and try the \
                                         program. If problem still persists, contact the developer.")
        quit_button = Button(cannot_register_class, text="QUIT", command=cannot_register_class.destroy)
        message.pack()
        quit_button.pack(anchor=SE)

    def timer_tk(self):
        failure_instance.withdraw()
        self.crn_instance.withdraw()
        timer_as_a_string = timer_setting.get()
        global timer_as_integer
        timer_as_integer = int(timer_as_a_string)
        global timer_instance
        timer_instance = Tk()
        timer_instance.title("Timer Standby")
        message = Message(timer_instance, text="Please keep this window open! as long as this window is open, it means\
the program is still trying to register your class at the time interval you input. Click RUN to start timer, click QUIT\
 to stop it")
        run_button_frame = Frame(timer_instance)
        run_button = Button(run_button_frame, text="RUN", command=lambda: timer(self.username, self.password,
                                                                                self.term, self.crn1))
        quit_button_frame = Frame(timer_instance)
        quit_button = Button(quit_button_frame, text="QUIT", command=timer_terminate_from_button)
        message.pack()
        run_button_frame.pack(side=RIGHT)
        run_button.pack(side=RIGHT)
        quit_button_frame.pack(side=LEFT)
        quit_button.pack(side=LEFT)

    def back_to_beginning_frame_from_entry_fields(self):
        """Goes back to first window from the class searching page"""
        entry_fields.destroy()
        self.__init__()

    def back_to_beginning_frame_from_crn_field(self):
        """Goes back to beginning frame from the CRN entry field"""

        self.crn_instance.destroy()
        self.__init__()


if __name__ == '__main__':
    acr = AutomaticClassRegistration()