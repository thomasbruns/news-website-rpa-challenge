import os
import logging
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

current_dir = os.path.dirname(os.path.abspath(__file__))
downloads_path = os.path.abspath(os.path.join(current_dir, '..', 'downloads'))


class CustomSelenium():

    def __init__(self, download_path=downloads_path):
        """
        Initialize the CustomSelenium instance.

        Parameters:
            - download_path: Path to the directory where files will be downloaded (default is downloads_path).
        """
        self.logger = logging.getLogger(__name__)
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-infobars')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )

    def open_url(self, url):
        """
        Open the specified URL in the web browser.

        Parameters:
            - url: The URL to be opened in the browser.
        """
        self.driver.get(url)

    def driver_quit(self):
        """
        Quit the web browser driver if it is currently active.
        """
        if self.driver:
            self.driver.quit()

    def search_xpath(self, xpath, timeout=10):
        """
        Wait for element identified by XPath to be present on the page.

        Parameters:
            - xpath: XPath expression to locate the elements
            - timeout: Maximum time to wait for the elements (default is 10 seconds)

        Returns:
            - WebElement: Located WebElement if found within the specified timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element

        except Exception as e:
            self.logger.warning(f"Unable to locate element: {xpath}")
            self.logger.warning(f"Error: {e}")
            return None

    def search_multiple_xpaths(self, xpath, timeout=10):
        """
        Wait for elements identified by XPaths to be present on the page.

        Parameters:
            - xpaths: List of XPath expressions to locate the elements
            - timeout: Maximum time to wait for the elements (default is 10 seconds)

        Returns:
            - List of WebElements: Located WebElements if found within the specified timeout
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                lambda d: d.find_elements(By.XPATH, xpath)
            )
            return elements

        except Exception as e:
            self.logger.warning(f"Unable to locate elements: {xpath}")
            self.logger.warning(f"Error: {e}")
            return None

    def select_from_dropdown(self, element, option):
        """
        Select an option from the dropdown using the specified WebElement and option text.

        Parameters:
            - element: WebElement representing the dropdown.
            - option: Text of the option to be selected.

        Returns:
            - bool: True if selection is successful, False otherwise.
        """
        try:
            sort_by = Select(element)
            sort_by.select_by_visible_text(option)
            return True

        except Exception as e:

            self.logger.warning(
                f"Unable to select {option} from dropdown with XPath: {dropdown_xpath}")
            self.logger.warning(f"Error: {e}")
            return False

    def move_to_element_then_click(self, element):
        """
        Move to the specified WebElement and perform a click action.

        Parameters:
            - element: WebElement to which the mouse will be moved before clicking.
        """
        try:
            ActionChains(self.driver).move_to_element(
                element).click().perform()

        except Exception as e:
            self.logger.warning(f"Error clicking element: {element}")
            self.logger.warning(f"Error: {e}")

    def press_enter(self, element):
        """
        Simulate pressing the 'Enter' key on the specified element.

        Parameters:
            - element: WebElement on which 'Enter' key will be pressed.
        """
        element.send_keys(Keys.RETURN)
