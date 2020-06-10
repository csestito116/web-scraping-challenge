from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time
import re


def scrape_all():
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }
    browser.quit()
    return data


def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    try:
        slide = soup.select_one("ul.item_list li.slide")
        title = slide.find("div", class_="content_title").get_text()
        news_p = slide.find(
            "div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    return title, news_p


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    image = browser.find_by_id("full_image")
    image.click()
    browser.is_element_present_by_text("more info", wait_time=0.5)
    data = browser.links.find_by_partial_text("more info")
    data.click()
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    img = soup.select_one("figure.lede a img")
    try:
        img_rel = img.get("src")
    except AttributeError:
        return None
    img = f"https://www.jpl.nasa.gov{img_rel}"
    return img

def hemispheres(browser):

    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )
    browser.visit(url)
    hemi_urls = []
    for i in range(4):
        browser.find_by_css("a.product-item h3")[i].click()
        hemi_data = scrape_hemisphere(browser.html)
        hemi_urls.append(hemi_data)
        browser.back()
    return hemi_urls

def twitter_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    time.sleep(5)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    tweet = {"class": "tweet", "data-name": "Mars Weather"}
    mars_tweet = soup.find("div", attrs=tweet)
    try:
        weather = mars_tweet.find("p", "tweet-text").get_text()
    except AttributeError:
        pattern = re.compile(r'sol')
        weather = soup.find('span', text=pattern).text
    return weather


def scrape_hemisphere(html_text):
    hemi_soup = BeautifulSoup(html_text, "html.parser")
    try:
        title = hemi_soup.find("h2", class_="title").get_text()
        sample = hemi_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title = None
        sample = None
    hemisphere = {
        "title": title,
        "img_url": sample
    }
    return hemisphere

def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None
    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)
    return df.to_html(classes="table table-striped")

if __name__ == "__main__":
    print(scrape_all())
