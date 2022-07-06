# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now()
    }

    # Quit the browser
    browser.quit()
    return data

### NASA NEWS SITE

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    # Account for attribute errors 
    except AttributeError:
        return None, None

    # Return the functioning news_title and paragraph
    return news_title, news_p



# ### JPL SPACE IMAGES FEATURED IMAGES

def featured_image(browser):

    # Visit URL for featured image
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    # Need to use index 1, because index 0 (the first button in the code) is a button that brings up nav menu. Index 1 is the featured image we want.
    full_image_button = browser.find_by_tag('button')[1]
    full_image_button.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Find the relative image url
    # the "fancybox-image" class is only present for the full-screen version of the featured image
    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Combine the base URL and relative image url to create a fully functional URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    # Return the functional URL
    return img_url


# ## Mars Facts

def mars_facts():

    # Use lxml and pandas to read in the html code from the galaxyfacts website and create a dataframe from the table
    # The [0] allows it to call on the first table in the code -- which happens to be a Mars/Earth comparison table
    # Would want to change index to [1] and columns to only [description,Mars] if we want the table at the top right of the page
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
        df.columns=['Description', 'Mars', 'Earth']
        df.set_index('Description', inplace=True)

    except BaseException:
        return None

    # Read the df back to html to make it compatible with future web app
    return df.to_html(classes='table table-striped')

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())