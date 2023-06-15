from Scrape_by_search import Scrape_by_search

url = "https://www.twitter.com/login"
mail = "instaeng.06@gmail.com"
user = "AlbertOne_Gar"
password = "Ridazzo1"
search_term = "russia"
y_scroll = 5

scrape = Scrape_by_search(url, mail, user, password, search_term, y_scroll)
scrape.execute()
