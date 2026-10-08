import requests
import bs4

def scrapper(urls, fields):

    for url in urls:
        req = requests.get(url)
        beautiful_soup = bs4.BeautifulSoup(req.text, "lxml")

        for field_key, field_value in fields.items():
            print(field_key)
            text_results = beautiful_soup.select(field_value)

            for text in text_results:
                if text.has_attr("title"):
                    print(text["title"])
                else:
                    print(text.get_text())
