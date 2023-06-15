import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import json
import time


class Scrape_by_search:
    def __init__(self, url, mail, user, password, search_term, y_scroll) -> None:
        self.url = url
        self.mail = mail
        self.user = user
        self.password = password
        self.search_term = search_term
        self.y_scroll = y_scroll
        self.driver = self.driver_init()

    def driver_init(self):
        DRIVER_PATH = "/chromedriver"
        url = self.url
        options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--disable-web-security")
        # options.add_argument("--window-size=1920,1200")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(options=options, service=Service(DRIVER_PATH))
        driver.get(url)
        wait = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located((By.NAME, "text"))
        )

        return driver

    def login(self, driver) -> None:
        driver.find_element(By.NAME, "text").send_keys(self.mail)
        wait = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@role='button']"))
        )
        buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
        buttons[2].click()
        wait = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located((By.NAME, "text"))
        )
        driver.find_element(By.NAME, "text").send_keys(self.user)
        buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
        buttons[1].click()
        wait = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located((By.NAME, "password"))
        )
        driver.find_element(By.NAME, "password").send_keys(self.password)
        driver.find_element(
            By.XPATH, "//div[@data-testid='LoginForm_Login_Button']"
        ).click()
        wait = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[text()='Refuse non-essential cookies']")
            )
        )
        driver.find_element(
            By.XPATH, "//span[text()='Refuse non-essential cookies']"
        ).click()

        time.sleep(3)

        json.dump(driver.get_cookies(), open("web_scraping/twitter/cookies.json", "w"))

    def search(self, driver) -> None:
        wait = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[@aria-label='Search query']")
            )
        )
        search = driver.find_element(By.XPATH, "//input[@aria-label='Search query']")
        search.send_keys(self.search_term)
        search.send_keys(Keys.ENTER)

    def tweets_links(self, driver) -> dict:
        html = {"title": "Tweets links", "links": []}
        for i in range(self.y_scroll):
            wait = WebDriverWait(driver, timeout=10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//article[@data-testid='tweet']")
                )
            )

            for tweet in driver.find_elements(
                By.XPATH, "//article[@data-testid='tweet']"
            ):
                wait = WebDriverWait(driver, timeout=10).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            "//div[@data-testid='User-Name']//div[2]//div//div[3]//a",
                        )
                    )
                )
                twe = tweet.find_element(
                    By.XPATH, "//div[@data-testid='User-Name']//div[2]//div//div[3]//a"
                )
                html["links"].append(twe.get_attribute("href"))

            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)

        html["links"] = list(set(html["links"]))

        with open(
            ("web_scraping/twitter/json_dump/{}_links.json").format(self.search_term),
            "w",
        ) as f:
            json.dump(html, f)
            f.close()

        return html

    def scrape(self, link, driver):
        driver.get(link)
        wait = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//article[1]//div[@data-testid='User-Name']//div[2]//div//div//a",
                )
            )
        )
        user_link = driver.find_element(
            By.XPATH, "//article[1]//div[@data-testid='User-Name']//div[2]//div//div//a"
        )
        user_link = user_link.get_attribute("href")
        user_link = user_link[20:]

        tweet_html = driver.find_element(
            By.XPATH, "//article[1]//div[1][@data-testid='tweetText']"
        )

        text = ""
        tweet_text = tweet_html.find_elements(By.TAG_NAME, "span")

        for row in tweet_text:
            text += row.get_attribute("innerHTML")

        time = tweet_html.find_element(By.XPATH, "//time[1]").get_attribute("datetime")
        tweets_dict = {"user": user_link, "text": text, "time": time}

        return tweets_dict

    def execute(self) -> None:
        if not os.path.isfile("web_scraping/twitter/cookies.json"):
            self.login(self.driver)
        else:
            cookies = json.load(open("web_scraping/twitter/cookies.json", "r"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.get("https://www.twitter.com/home")
        self.search(self.driver)
        tweets = self.tweets_links(self.driver)

        t_list = []

        for link in tweets["links"]:
            tweet = self.scrape(link, self.driver)
            t_list.append(tweet)

        with open(
            ("json_dump/{}_tweets.json").format(self.search_term),
            "w",
        ) as f:
            json.dump(t_list, f)
            f.close()
        self.driver.quit()
