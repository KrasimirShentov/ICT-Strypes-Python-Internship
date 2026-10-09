import requests
import bs4

def scrapper(urls, fields, page):

    for url in urls:
        req = requests.get(url)
        beautiful_soup = bs4.BeautifulSoup(req.text, "lxml")

        for field in fields:
            print(field)
            print(type(field))
            text_results = beautiful_soup.select(field)

            for text in text_results:
                if text.has_attr("title"):
                    print(text["title"])
                else:
                    print(text.get_text(strip=True))