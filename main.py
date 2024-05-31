from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import re
from datetime import datetime

# For sending email notifications
import smtplib
from email.mime.text import MIMEText

def main():

    # Initialize Driver
    service = Service()
    options = Options()
    dir = os.getcwd()
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9292")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    options.add_argument(f"--user-data-dir={dir}\\selenium-chrome-profile")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://cas.csufresno.edu/login?method=POST&service=https%3A%2F%2Fcmsweb.fresnostate.edu%2Fpsc%2FCFRPRD%2FEMPLOYEE%2FSA%2Fc%2FSA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL%3Fuserid%3Dsso_user%26pwd%3Dsso")

    # Get login form elements
    wait = WebDriverWait(driver=driver, timeout=10)
    user_form = wait.until(EC.presence_of_element_located((By.ID, 'username')))
    pswd_form = wait.until(EC.presence_of_element_located((By.ID, 'password')))
    login_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-info btn-lg btn-block btn-blue']")))


    # Fill out login fields -- change to your information
    user_form.send_keys('your_username') 
    pswd_form.send_keys('your_password')
    login_btn.click()

    # Regular expressions to match either the auth url or fresno state target page
    URL_duo_re = '.*duosecurity.com/frame/v4/auth/.*' 
    URL_fs_re  = 'https://cmsweb.fresnostate.edu/psc/CFRPRD/EMPLOYEE/SA/.*'

    def wait_for_url(url: str) -> bool:
        duo_match = re.match(URL_duo_re, url)
        fs_match = re.match(URL_fs_re, url)
        if duo_match or fs_match:
            return False # Once page is loaded, break 
        return True

    # Wait till page loads or duo mobile prompt
    while (wait_for_url(driver.current_url)):
        sleep(0.5)
        print("waiting for page redirect")
        continue

    # Check if 2fa needs to be activated
    if re.match(URL_duo_re, driver.current_url):
        # Wait 5 seconds for duo to load
        print("Duo is loading...")
        sleep(5)

        # Wait for user duo mobile authentication 20 seconds before timeout)
        auth_wait = WebDriverWait(driver=driver, timeout=20)
        print("created auth_wait")                   
        try:
            print("Waiting for duo authentication")
            continue_btn = auth_wait.until(EC.presence_of_element_located((By.ID, 'trust-browser-button')))
            print("found continue button")
            continue_btn.click()
        except Exception as e:
            print("could not find continue button, continuing...")
        
        print("Signed in!")

        # In case we need to wait for redirect after duo auth
        while (wait_for_url(driver.current_url)):
            sleep(0.5)
            print("waiting for page redirect")
            continue

    # Check if it was successful
    if re.match(URL_fs_re, driver.current_url):
        print("SUCCESS")
    else:
        #if unsuccessful, quit
        print("UNSUCCESSFUL")
        driver.quit()
        return 
    
    # Navigate to semester (currently hardcoded to fall 2024, may have to change)
    fall2024_btn = wait.until(EC.presence_of_element_located((By.ID, 'SSR_DUMMY_RECV1$sels$1$$0')))
    fall2024_btn.click()
    continue_btn = wait.until(EC.presence_of_element_located((By.ID, 'DERIVED_SSS_SCT_SSR_PB_GO')))
    continue_btn.click()

    wait.until(EC.title_is('Enrollment Shopping Cart'))

    # Returns true if a course is open
    def courseIsOpen(courseID: str):
        # Finding the reference element of the course is currently hardcoded to the third class in the wishlist
        #    You can change which class in the wishlist it targets by changing the last digit in 'P_CLASS_NAME$2' 
        #    to the index of the class you want to check (0 indexed). 
        ref = wait.until(EC.presence_of_element_located((By.ID, 'P_CLASS_NAME$2'))) 
        ref.click()

        # Wrap this in a try block, it will only be successful if the class has a required lab section attached
        try:
            continue_btn = wait.until(EC.presence_of_element_located((By.ID, 'DERIVED_CLS_DTL_NEXT_PB')))
            continue_btn.click()
        except Exception as e:
            pass
        finally:
            print("continuing...")
        
        status = wait.until(EC.presence_of_element_located((By.ID, 'DERIVED_CLS_DTL_SSR_DESCRSHORT$0')))
        if 'Closed' in status.get_attribute('innerHTML'):
            return False
        else:
            return True


    course_IDs = ['72390'] #TODO: make course search dynamic to support multiple classes -- right now this does nothing

    # Check every 5 minutes
    while(True):
        for id in course_IDs:
            if courseIsOpen(id):
                print(f'COURSE {id} is OPEN, Sending email...')
                email = "sender_email@gmail.com"
                password = "gmail_password" # Note: Probably have to use app password
                msg = MIMEText('It\'s open, enroll now!!!')
                msg['Subject'] = 'YOUR CLASS IS OPEN'
                msg['From'] = email
                msg['To'] = email

                # Send the message via gmail server.
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                    smtp_server.login(email, password=password)
                    smtp_server.sendmail(email, email, msg.as_string())
                print("Email sent! Shutting down...")
                driver.quit()
                return
            else:
                currentTime = datetime.now().time()
                print(f'COURSE {id} is CLOSED {currentTime}')

            continue_btn = wait.until(EC.presence_of_element_located((By.ID, 'DERIVED_CLS_DTL_NEXT_PB')))
            continue_btn.click()
        sleep(300)


if __name__ == '__main__':
    main()