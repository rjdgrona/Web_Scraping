from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import datetime as dt

def scrape_all():

    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_pa = mars_news(browser)
    data = {
        "news_title": news_title,
        "news_paragraph": news_pa,
        "featured_image": mars_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": mars_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }
    browser.quit()
    return data

def mars_news(browser):
   #URL or pages to be scraped
    url_marsnews = "https://mars.nasa.gov/news/"

    # Retrieve page with the requests module
    response_marsnews = requests.get(url_marsnews)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup_marsnews = bs(response_marsnews.text, 'html.parser')


    #Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text. 
    news_list_soup = soup_marsnews.find_all('div', class_="slide")
    for news in range(1) :
        news_title = news_list_soup[news].find('div', class_="content_title").text.strip()
        news_pa = news_list_soup[news].find('div', class_="rollover_description_inner").text.strip()
 
    return news_title, news_pa

def mars_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    #Scrape for the full image
    browser.find_by_id("full_image").click()
    browser.is_element_present_by_text('more info')
    more_info_element = browser.find_link_by_partial_text('more info')
    more_info_element.click()
    html = browser.html
    image_soup = bs(html, 'html.parser')
    img = image_soup.select_one('figure.lede a img')
    try:
        img_url = img.get("src")

    except AttributeError:
        return None

    #Get the image URL
    featured_image_url  = f'https://www.jpl.nasa.gov{img_url}'
    return featured_image_url

def mars_weather(browser):
    #URL or pages to be scraped
    url_weather = "https://twitter.com/marswxreport"

    # Retrieve page with the requests module
    response_weather= requests.get(url_weather)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup_weather = bs(response_weather.text, 'lxml')

    #Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text. 
    weather_soup = soup_weather.find_all('div', class_="js-tweet-text-container")
    for weather in range(1) :
        mars_weather = weather_soup[weather].find('p').text

    return mars_weather

def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)
    return df.to_html(classes="table table-striped")

def hemispheres(browser):

    hem_url ="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hem_url)

    hemisphere_image_urls = []
    for i in range(4):
        browser.find_by_css("a.product-item h3")[i].click()
        hemi_data = scrape_hemisphere(browser.html)
        hemisphere_image_urls.append(hemi_data)
        browser.back()
    return hemisphere_image_urls


def scrape_hemisphere(html_text):
    hemi_soup = bs(html_text, "html.parser")
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title_elem = None
        sample_elem = None
    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }
    return hemisphere

if __name__="__main__":
    print(scrape_all())