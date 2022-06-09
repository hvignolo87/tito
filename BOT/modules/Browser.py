# Load useful classes
import sys

import os

# Import Installer for missing packages
if __name__ == '__main__':
    from Installer import Installer
else:
    from .Installer import Installer

try:
    # Import Selenium if installed
    from selenium import webdriver
except ModuleNotFoundError:
    # If not installed, install it
    Installer('selenium', True).install()

try:
    from fake_useragent import UserAgent
except ModuleNotFoundError:
    # If not installed, instalrl it
    Installer('fake_useragent').install()

try:
    import undetected_chromedriver as uc
except ModuleNotFoundError:
    # If not installed, install it
    Installer('undetected-chromedriver').install()

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ModuleNotFoundError:
    # If not installed, install it
    Installer('webdriver-manager').install()

# Selenium useful modules
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# Webdriver Manager
from webdriver_manager.chrome import ChromeDriverManager

# Undetectable Chrome
import undetected_chromedriver as uc

# Fake the User Agent
from fake_useragent import UserAgent

# Simplified class to perform scrapping
class Browser:
    """
    Browser Handler \n
    This class allows to friendly interact with any website via Selenium.

    Parameters
    ----------
    undetectable : bool
        - Flag to switch to undetectable mode if needed.
    
    Attributes
    ----------
    url : str
        - The URL, including protocol.
    wait_time : int
        - Number of seconds to wait for an HTML is loaded.

    Methods
    -------
        go_to(url='')
        Redirects to the specified URL.

        find_and_click(by='', value='')
        Finds a HTML element, then click on it.
            
        find_fill_submit(by='', value='', keys='', submit=False)
        Finds a HTML element, fill it with text and submit it (if it's a form).

        handle_popup(action='', keys=''):
        Handles a popup window.

        close_browser()
        Quits the driver instance, closing every associated window, which is opened.
    """

    # Constructor of the browser handler
    def __init__(self, undetectable: bool = False) -> None:
        """Constructor of the class

        Parameters
        ----------
        undetectable : bool
            - Flag to switch to undetectable mode if needed
        """

        self.__check_args(undetectable, bool)

        # Undetectable flag
        self._undetectable = undetectable

        # Set the options to avoid detection
        self._options = self.__set_options()

        # Set the wait time
        self.wait_time = 5

        # Avoid SSL Certificate verification
        os.environ['WDM_SSL_VERIFY'] = '0'

        # Create the driver instance
        if not undetectable:
            # Set the driver
            self._driver = webdriver.Chrome(
                service=Service(
                    ChromeDriverManager().install()
                ),
                options=self._options
            )
        else:
            # Set the driver
            self._driver = uc.Chrome(options=self._options)

        # Avoid detection
        self._driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", 
                                    {"source":
                                    "const newProto = navigator.__proto__;"
                                    "delete newProto.webdriver;"
                                    "navigator.__proto__ = newProto;"})

        self._driver.execute_cdp_cmd('Network.setUserAgentOverride', 
                                    {"userAgent": self._user_agent})
        return None

    # Define options of the browser in order to avoid detection
    def __set_options(self) -> object:
        """Set the browser options in order to avoid detection
        """

        # Set a random user agent in order to avoid captcha
        self._user_agent = UserAgent().random

        if self._undetectable:
            return uc.ChromeOptions()
        else:
            # Instantiate a options object of Chrome
            opt = webdriver.ChromeOptions()
            
            # Set some options
            opt.add_argument('--start-maximized')
            #opt.add_argument('--single-process')
            opt.add_argument('--incognito')
            opt.add_argument('--disable-gpu')
            opt.add_argument('--no-sandbox')
            opt.add_argument('--disable-blink-features')
            opt.add_argument('--disable-blink-features=AutomationControlled') 
            opt.add_argument('--disable-dev-shm-usage')
            opt.add_argument('--disable-impl-side-painting')
            opt.add_argument('--disable-setuid-sandbox')
            opt.add_argument('--disable-seccomp-filter-sandbox')
            opt.add_argument('--disable-breakpad')
            opt.add_argument('--disable-client-side-phishing-detection')
            opt.add_argument('--disable-cast')
            opt.add_argument('--disable-cast-streaming-hw-encoding')
            opt.add_argument('--disable-cloud-import')
            opt.add_argument('--disable-popup-blocking')
            opt.add_argument('--ignore-certificate-errors')
            opt.add_argument('--disable-session-crashed-bubble')
            opt.add_argument('--disable-ipv6')
            opt.add_argument('--allow-http-screen-capture')
            opt.add_experimental_option('useAutomationExtension', False)
            opt.add_experimental_option('excludeSwitches', ['enable-automation'])
            opt.add_experimental_option('excludeSwitches', ['enable-logging'])
            opt.add_argument('--disable-infobars')
            opt.add_argument('--user-agent={}'.format(self._user_agent))
            return opt

    # Find and HTML element
    def __find_element(self, by: str = '', value: str = '') -> object:
        """Finds a HTML element in a website.
        
        Parameters
        ----------
        by : str
            - How will Selenium search for the element.
            - Possible values: id, link_text, xpath, class_name.
            
        value : str
            - HTML parameter to find the element.
        """

        self.__wait_element_load(by=by, value=value)

        if by.lower() == 'id':
            return self._driver.find_element(by=By.ID, value=value)
        elif by.lower() == 'link_text':
            return self._driver.find_element(by=By.LINK_TEXT, value=value)
        elif by.lower() == 'xpath':
            return self._driver.find_element(by=By.XPATH, value=value)
        elif by.lower() == 'class_name':
            return self._driver.find_element(by=By.CLASS_NAME, value=value)
        return None

    # Find more than one element
    def find_elements(self, by: str = '',
                      value: str = '', 
                      wait: bool = True) -> object:
        """Finds various HTML elements in a website.
        
        Parameters
        ----------
        by : str
            - How will Selenium search for the elements.
            - Possible values: xpath, class_name, css_selector.
            
        value : str
            - HTML parameter to find the elements.

        wait : bool
            - Whether or not wait until the element is present in the page.
        """        
        if wait:
            self.__wait_element_load(by=by, value=value)
        else:
            self.__check_args(by, str)
            self.__check_args(value, str)

        if by.lower() == 'class_name':
            return self._driver.find_elements_by_class_name(value)
        elif by.lower() == 'xpath':
            return self._driver.find_elements_by_xpath(value)
        elif by.lower() == 'css_selector':
            return self._driver.find_elements_by_css_selector(value)

        return None
    
    # Validate arguments
    def __check_args(self, args: str = '', 
                     instance: [object, list] = '') -> None:
        """Method to validate arguments
        
        Parameters
        ----------
        args : str
            - Argument to check
        instance : object or list
            - Instance for checking
        """
        if isinstance(instance, list):
            for i in instance:
                if not isinstance(args, i) or args == '':
                    print("Argument is empty or wrong. Shutting down.")
                    sys.exit()
                else:
                    continue
        else:
            if not isinstance(args, instance) or args == '':
                print("Argument is empty or wrong. Shutting down.")
                sys.exit()
        return None

    # Go to specific URL
    def go_to(self, url: str = '') -> None:
        """Redirects to specified URL.\n
        If the argument ``url`` is not a string or it's empty, the scripts ends.

        Parameters
        ----------
        url : str
            - The URL to redirect, including protocol.
        """
        self.__check_args(url, str)
        self._url = url
        self._driver.get(url=self._url)
        return None

    # Find and click a HTML element
    def find_and_click(self, by: str = '', value: str = '') -> None:
        """Find a HTML element and click on it.\n
        If the arguments ``by`` or ``value`` is not a string or it's empty, the scripts ends.

        Parameters
        ----------
        by : str
            - How will Selenium search for the element. Possible values: id, link_text, xpath
        value : str
            - HTML parameter to find the element.
        """
        self.__check_args(by, str)
        self.__check_args(value, str)
        self.__find_element(by=by, value=value).click()
        return None

    # Find a HTML element, fill it with text, then submit
    def find_fill_submit(self, by: str = '', 
                         value: str = '', keys: [str, list] = '', 
                         submit: bool = False) -> None:
        """Find a HTML element, fill it with text and submit (if it's a form). \n
        If the arguments ``by`` or ``value`` aren't strings or are empty, the scripts ends.

        Parameters
        ----------
        by : str
            - How will Selenium search for the element. Possible values: id, link_text, xpath
        value : str
            - HTML parameter to find the element.
        """
        self.__check_args(by, str)
        self.__check_args(value, str)
        self.__check_args(keys, (str, list))
        
        element = self.__find_element(by=by, value=value)

        if  isinstance(keys, str):
            element.send_keys(keys)
        elif isinstance(keys, list):
            element.send_keys(keys[0])
            if keys[1].lower() == 'return':
                element.send_keys(Keys.RETURN)

        if submit:
            element.submit()
            return None

        return None

    def __wait_element_load(self, by: str = '', value: str = '') -> None:
        """Wait until a HTML element is loaded. \n
        If the arguments ``by`` or ``value`` aren't strings or are empty, the scripts ends.

        Parameters
        ----------
        by : str
            - How will Selenium search for the element.Possible values: id, link_text, xpath, class_name
        value : str
            - HTML parameter to find the element.
        """
        self.__check_args(by, str)
        self.__check_args(value, str)

        if by.lower() == 'id':
            locator = (By.ID, value)
        elif by.lower() == 'link_text':
            locator = (By.LINK_TEXT, value)
        elif by.lower() == 'xpath':
            locator = (By.XPATH, value)
        elif by.lower() == 'class_name':
            locator = (By.CLASS_NAME, value)
        elif by.lower() == 'css_selector':
            locator = (By.CSS_SELECTOR, value)
        else:
            return None

        try:
            WebDriverWait(self._driver, self.wait_time) \
            .until(EC.presence_of_element_located(locator))
        except:
            pass
        else:
            return None

        try:
            WebDriverWait(self._driver, self.wait_time) \
            .until(EC.presence_of_all_elements_located(locator))
        except:
            print('HTML element not located. Shutting down.')
            sys.exit()

        return None
    
    def handle_popup(self, action: str = '', keys: str = '') -> None:
        """Handles a popup. \n
        If the argument ``action`` isn't a string or is empty, the scripts ends.

        Parameters
        ----------
        action : str
            - The action to take. 
            - Possible values: *accept*, *dissmiss*, *get_text*, *send_keys*
            - If takes the value *send_keys*, ``keys`` must be pass.
        keys : str
            - The string to fill the popup
            - Used only if ``action`` = 'send_keys'
        """
        
        # Wait until the popup shows
        WebDriverWait(self._driver, self.wait_time).until(EC.alert_is_present())
        
        # Lowercase
        action = action.lower()
        keys = keys.lower()

        # All posible values for the action
        values = ['accept', 'dissmiss', 'get_text', 'send_keys']

        # Validate argument
        self.__check_args(action, str)

        # If invalid parameter is passed, shut down
        if action not in values:
            self.__check_args()
        elif action == 'send_keys':
            self.__check_args(keys, str)

        # Perform the action
        if action == 'accept':
            self._driver.switch_to.alert.accept()
            return None
        elif action == 'dismiss':
            self._driver.switch_to.alert.dismiss()
            return None
        elif action == 'get_text':
            return self._driver.switch_to.alert.text
        elif action == 'send_keys':
            self._driver.switch_to.alert.send_keys(keys)
            self._driver.switch_to.alert.accept()
            return None
    
    def close_browser(self) -> None:
        """
        Quits the driver instance, closing
        every associated window, which is opened.
        """
        self._driver.quit()
        return None