# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    #executable_path = {'executable_path': '/Users/gabrielaeavalos/Applications/chromedriver'}
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
            "news_title": news_title,
            "news_paragraph": news_paragraph,
            "featured_image": featured_image(browser),
            "facts": mars_facts(),
            "hemispheres": mars_hemisphers(browser),
            "last_modified": dt.datetime.now(),
        }
    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
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

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemisphers(browser):
    url = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/index.html'

    browser.visit(url)

    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')

    hemispheres = hemisphere_soup.find_all('div', class_='item')

    hemisphere_image_urls = []

    hemispheres_url = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/'

    for i in hemispheres:
        #hemisphere = {}

        title =  i.find('h3').text

        ending_img_url = i.find('a', class_='itemLink product-item')['href']
        browser.visit(hemispheres_url + ending_img_url)
        img_html = browser.html
        img_soup = soup(img_html, 'html.parser')
        img_url = hemispheres_url + img_soup.find('img', class_='wide-image')['src']

        hemisphere_image_urls.append({'img_url': img_url, 'title': title})
        
        print(hemisphere_image_urls)

        # try:
        #     thumbnail= browser.find_by_tag('h3')[i]
        #     thumbnail.click()

        #     # Parse the hemisphere page with soup
        #     html = browser.html
        #     img_soup = soup(html, 'html.parser')

        #     # Find the relative image url and nama
        #     img_url = img_soup.find('img', class_='wide-image').get('src')
        #     img_name= img_soup.find('h2').get_text()

        #     #append to hemisphere dict
        #     hemisphere[img_url] = img_name
        #     hemisphere_image_urls.append(hemisphere)
        # except Exception:
        #     pass
        # link = browser.find_link_by_href('index.html')

        #link.click()

    return hemisphere_image_urls
    #print(hemisphere_image_urls)



 

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
