import requests
import bs4

def scrapper(urls, fields, page, url_format):
    template_url = url_format
    
    for page_num in range(1, page + 1):
        url_format = template_url.format(page_num)
        req = requests.get(url_format)
        beautiful_soup = bs4.BeautifulSoup(req.text, "lxml")


        for field in fields:
            text_results = beautiful_soup.select(field)

            for text in text_results:
                if text.has_attr("title"):
                    print(text["title"])
                else:
                    print(text.get_text(strip=True))
        
            print()
