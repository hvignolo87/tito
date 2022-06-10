# Libraries for handling configuration, time and paths
import configparser
import time
import os
import sys

"""
# TITO
Bot used to book a day to request italian citizenship (by any method) or passport at Prenot@Mi website.
In order to making it work, you need to create a configuration file, like explained [here](https://github.com/hvignolo87/tito/blob/main/README.md).
"""

# Import all modules
from modules import *
from datetime import datetime
from io import StringIO

try:
    # Import streamlit for front end
    import streamlit as st
except ModuleNotFoundError:
    # If not installed, install it
    Installer('streamlit').install()

# Start the script
def tito(uploaded_file, check_hour):

    st.write('TITO started!')

    #/*** LOAD DATA FROM INI FILE ***/
    # Read data from .ini file
    config = configparser.ConfigParser()

    config.read_file(uploaded_file)
    
    # Prenot@Mi e-mail
    EMAIL = config['PRENOTAMI_DATA']['email']

    # Prenot@Mi password
    PASSWORD = config['PRENOTAMI_DATA']['pass']

    # Service required
    SERVICE = config['PRENOTAMI_DATA']['service']

    # OTP code insertion delay
    OTP_DELAY_TIME = int(config['PRENOTAMI_DATA']['otp_delay'])

    # The form data
    FORM_DATA = config[SERVICE.upper()]



    #/*** GET INTO PRENOTAMI WEBPAGE AND LOGIN ***/
    # Create the instance of the browser
    browser = Browser()

    # Create the Web Page object to retrieve locators
    web_page = PrenotamiWebPage(service=SERVICE)

    # Get the URL
    browser.go_to(url=web_page.get_url())
    
    # Locate login form
    loc = web_page.get_locator('login')
    
    # Search for the e-mail field and fill it
    browser.find_fill_submit(by=loc['BY'], 
                             value=loc['LOGIN_EMAIL'], 
                             keys=EMAIL)

    # Search for the pass field, fill it and submit the form
    browser.find_fill_submit(by=loc['BY'], 
                             value=loc['LOGIN_PASSWORD'], 
                             keys=[PASSWORD, 'RETURN'])

    # Delete the variable
    del(loc)



    #/*** GO TO BOOK SECTION AND CLICK ON THE SERVICE ***/
    # Locate book link
    loc = web_page.get_locator('user_area')

    # Click on book tab
    browser.find_and_click(by=loc['BY'], value=loc['USERAREA_PRENOTA'])

    # Delete the variable
    del(loc)

    # Check if it's time to start
    if check_hour:
        st.write('Checking the hour...')
        now = datetime.now()
        init_hour = datetime.now().replace(hour=19, minute=00, 
                                           second=0, microsecond=0)
        diff = init_hour - now
        # Remove some seconds in order to improve performance
        diff = diff.total_seconds() - 3

        if diff >= 0:
            st.write(f'Waiting until {init_hour}...')
            st.write(f'Time left: {diff} seconds.')
            time.sleep(diff)
            st.write("It's time! Go!")
        else:
            print('Too late. Try again tomorrow.')
            browser.close_browser()
            sys.exit()

    # Locate the required service button
    loc = web_page.get_locator(SERVICE)

    # Click on the service
    browser.find_and_click(by=loc['BY'], value=loc['SERVICE_BUTTON'])
    


    #/*** FILL THE FORM AND SUBMIT ***/
    
    # Fill the form with the specified data
    for field in FORM_DATA:
        try:
            browser.find_fill_submit(by=loc['BY'], 
                                     value=loc[field.upper()], 
                                     keys=FORM_DATA[field])
        except:
            continue

    # Check the terms and conditions
    browser.find_and_click(by=loc['BY'], value=loc['CHECKBOX'])
    
    # Submit the form
    browser.find_and_click(by=loc['BY'], value=loc['SUBMIT'])
    
    # Press OK in the popup window
    browser.handle_popup(action='accept')

    # Delete the variable
    del(loc)



    #/*** CALENDAR SECTION: FIND AN AVAILABLE DAY AND BOOK ***/

    # Locate the calendar buttons: backwards, month and forward
    loc = web_page.get_locator('calendar')

    # Flag to indicate whether is any day available in the month or no
    no_available_days = True

    # Initialize assuming no green days available
    green_days = []

    # Try for max 18 months
    max_tries = 18

    # Count each iteration
    iter_count = 0

    # Iterate the calendar until find and available day
    while no_available_days:
        try:
            # Find all the available days in a month
            green_days = browser.find_elements(by='class_name', 
                                               value=loc['GREEN_DAYS'])
            if green_days == None:
                green_days = []
        except:
            pass
        
        # Logic to walk around the months
        if not len(green_days):
            # Compare iteration number with stop limit
            if iter_count > max_tries:
                # No available days within 18 months
                no_available_days = False
                # Print a message
                st.write('No days available within next 18 months.')
            else:
                # Continue searching for available days in next month
                browser.find_and_click(by=loc['BY'], value=loc['FORWARD'])
                # Sum one iteration
                iter_count += 1
                # Print the count
                st.write(f'Remaining attempts: {max_tries-iter_count}')
                # Wait until everything is loaded
                time.sleep(2)
                # Continue the loop
                continue
        else:
            # Change the flag
            no_available_days = False

            # Click on the first available day
            green_days[0].click()

            # Find the first available hour
            hours = browser.find_elements(by='class_name', value=loc['HOURS'])

            # Click on the first available hour
            hours[0].click()

            # Submit the form
            browser.find_and_click(by=loc['BY'], value=loc['SUBMIT'])

            # If there is an OTP code to insert, wait until the user writes it
            try:
                otp = browser.find_elements(by=loc['BY'], value=loc['OTP'])
            except:
                pass
            else:
                # Click on the input of the OTP window
                otp[0].click()
                
                # Get the OTP ok button
                otp_ok = browser.find_elements(by=loc['BY'], 
                                               value=loc['OTP_OK'])
                
                # Wait until the user inserts the OTP code
                time.sleep(OTP_DELAY_TIME)
                
                # Submit the OTP form
                otp_ok[0].click()

                # Print a message
                st.write('Process succeed!')
    
    # Wait a long time to ensure the procces is ended
    time.sleep(10)

    # Close the browser
    browser.close_browser()

    # Then, end the script
    sys.exit()

if __name__ == '__main__':
    
    """
    #### 1. Load the configuration file
    """
    uploaded_file = st.file_uploader(
        label='Load configuration file (user_data.ini)',
        type='.ini',
        help="If you don't know how to create the configuration file, please \
              visit: https://github.com/hvignolo87/tito/blob/main/README.md"
    )

    """
    #### 2. Do you want to set the hour check mode?
    This mode enable automatic check of the hour. When 19hs (ART) comes, the bot is launched automatically.

    If you don't want to wait, or just want to perform some tests, select ```no```.
    """
    check_hour = st.radio(
        label="Enable hour check mode",
        options=('Yes', 'No')
    )

    check_hour = True if check_hour == 'Yes' else False

    """
    #### 3. Run the bot
    """
    if st.button('Click here to run!') and uploaded_file:
        uploaded_file_io = StringIO(uploaded_file.getvalue().decode('utf-8'))
        try:
            tito(uploaded_file_io, check_hour)
        except:
            st.write('Something went wrong, please try again later.')
    else:
        st.write('First complete the above steps.')