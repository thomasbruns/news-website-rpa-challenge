from custom_selenium import CustomSelenium
from datetime import datetime
import dateutil.relativedelta
import urllib.request
import pandas as pd
import logging
import time
import re
import os

logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
downloads_path = os.path.abspath(os.path.join(current_dir, '..', 'downloads'))
data_output_path = os.path.abspath(
    os.path.join(current_dir, '..', 'data', 'output'))


def accept_cookies(driver):
    """
    Accept cookies by locating and clicking the 'Accept all' button on the webpage.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.
    """
    cookie_buttons = driver.search_multiple_xpaths(
        '//*[@id="fides-banner-button-primary"]')
    time.sleep(1)
    for cookie_button in cookie_buttons:
        if cookie_button.get_attribute("innerText") == "Accept all" and cookie_button.is_displayed():
            cookie_button.click()
            break


def search_for_keyphrase(driver, keyphrase):
    """
    Perform a search for the specified keyphrase on the webpage.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.
        - keyphrase: The keyphrase to be searched.
    """
    search_button = driver.search_xpath(
        '//*[@id="app"]/div[2]/div[2]/header/section[1]/div[1]/div[2]')
    search_button.click()
    search_text_box = driver.search_xpath(
        '//*[@id="search-input"]/form/div/input')
    search_text_box.click()
    search_text_box.clear()
    search_text_box.send_keys(keyphrase)
    driver.press_enter(search_text_box)


def select_section(driver, desired_section):
    """
    Select a specific section on the webpage.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.
        - desired_section: The name of the section to be selected.
    """
    section_button = driver.search_xpath(
        '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[2]/div/div/button')
    section_button.click()
    sections = driver.search_multiple_xpaths(
        '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[*]')
    for section in sections:
        if (desired_section in section.get_attribute("innerText")) and not section.is_selected():
            section.click()
            break
    section_button.click()


def sort_by_newest(driver):
    """
    Sort the content on the webpage by the newest items.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.

    Returns:
        - bool: True if sorting is successful, False otherwise.
    """
    sort_by_box = driver.search_xpath(
        '//*[@id="site-content"]/div/div[1]/div[1]/form/div[2]/div/select')

    item_selected = driver.select_from_dropdown(
        element=sort_by_box, option='Sort by Newest')

    return item_selected


def locate_news(driver):
    """
    Locate and return a list of news elements on the webpage.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.

    Returns:
        - List of WebElements: Located WebElements representing news items.
    """
    news_elements = driver.search_multiple_xpaths(
        '//*[@id="site-content"]/div/div[2]/div[*]/ol/li[*]')
    return news_elements


def parse_date(date_string):
    """
    Parse a date string into a datetime object.

    Parameters:
        - date_string: String representation of a date.

    Returns:
        - datetime: Parsed datetime object.
    """
    if ',' not in date_string:
        date_string += f', {datetime.now().year}'

    date_format = "%b %d, %Y"

    month_string, day_and_year_string = date_string.split('.')

    date_object = datetime.strptime(
        month_string[:3] + day_and_year_string, date_format)

    return date_object


def show_more_until_date_reached(driver, target_date):
    """
    Click the 'Show more' button on the webpage until the target date is reached.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.
        - target_date: Target date to stop showing more news.

    Returns:
        - None
    """
    target_date_reached = False

    while not target_date_reached:

        news_elements = locate_news(driver)

        oldest_news_visible = news_elements[-1]
        date_string = oldest_news_visible.get_attribute(
            "innerText").split('\n')[0]
        oldest_news_date = parse_date(date_string)
        if oldest_news_date <= target_date:
            break
        else:
            show_more_button = driver.search_xpath(
                '//*[@id="site-content"]/div/div[2]/div[*]/div/button')
            driver.move_to_element_then_click(show_more_button)
            time.sleep(1)


def check_money_string_on_news(news_title, news_description):
    """
    Check if a money pattern is present in the news title or description.
    Possible formats: $11.1 | $111,111.11 | 11 dollars | 11 USD

    Parameters:
        - news_title: Title of the news.
        - news_description: Description of the news.

    Returns:
        - bool: True if money pattern is found, False otherwise.
    """
    money_pattern = r'\$\d+(\.\d{1,2})?|\d+(\.\d{1,2})?\s?(dollars|USD)'

    if re.search(money_pattern, news_title) or re.search(money_pattern, news_description):
        return True
    else:
        return False


def count_search_phrase(news_title, news_description, search_phrase):
    """
    Count the occurrences of a search phrase in the news title and description.

    Parameters:
        - news_title: Title of the news.
        - news_description: Description of the news.
        - search_phrase: The phrase to be counted.

    Returns:
        - int: Total count of the search phrase.
    """
    title_count = news_title.lower().count(search_phrase.lower())
    description_count = news_description.lower().count(search_phrase.lower())

    total_count = title_count + description_count
    return int(total_count)


def download_image(driver, element_id, picture_filename):
    """
    Download the image associated with a news element.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.
        - element_id: ID of the news element.
        - picture_filename: Filename to save the downloaded image.

    Returns:
        - bool: True if the image is successfully downloaded, False otherwise.
    """
    image_xpath = (
        f'//*[@id="site-content"]/div/div[2]/div[*]/ol/li[{element_id}]/div/div/figure/div/img')
    image_element = driver.search_xpath(image_xpath)
    try:
        image_url = image_element.get_attribute('src')
        urllib.request.urlretrieve(image_url, os.path.join(
            downloads_path, f'{picture_filename}.jpg'))
        return True
    except AttributeError as e:
        logger.info(f'Could not retrieve image from xpath: {image_xpath}')
        logger.info(f'Error: {e}')
        return False


def get_news_data(driver, months_range, test_keyphrase):
    """
    Retrieve news data from the webpage.

    Parameters:
        - driver: CustomSelenium instance representing the web browser driver.
        - months_range: Number of months to go back in time for news data.
        - test_keyphrase: Keyphrase to search for in the news.

    Returns:
        - DataFrame: Pandas DataFrame containing news data.
    """
    months_range -= 1
    if months_range == -1:
        months_range = 0

    current_date = datetime.now()
    first_day_of_current_month = current_date.replace(day=1)
    earliest_possible_date = first_day_of_current_month - \
        dateutil.relativedelta.relativedelta(months=months_range)

    news_data = {
        'Title': [],
        'Date': [],
        'Description': [],
        'Picture filename': [],
        'Count of search phrase': [],
        'Has money': []
    }

    news = pd.DataFrame(data=news_data)

    show_more_until_date_reached(driver, earliest_possible_date)

    news_elements = locate_news(driver)

    element_id = 1

    for news_element in news_elements:

        if news_element.get_attribute('className') != 'css-1l4w6pd':
            pass
        else:
            if 'ADVERTISEMENT' not in news_element.get_attribute("innerText"):

                news_date_string = news_element.get_attribute(
                    "innerText").split('\n')[0]
                news_date = parse_date(news_date_string)
                if news_date.date() < earliest_possible_date.date():
                    break
                else:
                    news_data['Title'] = news_element.get_attribute(
                        "innerText").split('\n')[4]
                    news_data['Date'] = news_date
                    news_data['Description'] = news_element.get_attribute(
                        "innerText").split('\n')[6]
                    news_data['Picture filename'] = f'news_image{element_id}'
                    news_data['Count of search phrase'] = count_search_phrase(
                        news_data['Title'], news_data['Description'], test_keyphrase)
                    news_data['Has money'] = check_money_string_on_news(
                        news_data['Title'], news_data['Description'])
                    if not download_image(driver, element_id, news_data['Picture filename']):
                        news_data['Picture filename'] = ''
                    news = pd.concat(
                        [news, pd.DataFrame(data=news_data, index=[0],)], ignore_index=True)

            element_id += 1

    news['Count of search phrase'] = news['Count of search phrase'].astype(int)
    news['Has money'] = news['Has money'].astype(bool)
    news['Date'] = news['Date'].dt.strftime('%Y-%m-%d')
    return news


def main(test_keyphrase='bitcoin', news_section='Business', months_range=3):

    website_url = 'https://www.nytimes.com'

    driver = CustomSelenium()

    driver.open_url(website_url)

    accept_cookies(driver)
    search_for_keyphrase(driver, test_keyphrase)
    select_section(driver, news_section)
    if sort_by_newest(driver):
        time.sleep(1)
        news = get_news_data(driver, months_range, test_keyphrase)
        excel_filename = 'news_data.xlsx'
        news.to_excel(os.path.join(data_output_path,
                      excel_filename), index=False)
    else:
        logger.info("Could not sort by newest")

    driver.driver_quit()


if __name__ == '__main__':
    main()
