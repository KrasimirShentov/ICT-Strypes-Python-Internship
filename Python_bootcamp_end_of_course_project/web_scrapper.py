import requests
import bs4

def scrapper(fields, field_names, page, url_format, item_selector):
    results = dict()

    for page_num in range(1, page + 1):
        page_url = url_format.format(page_num)
        page_results = []

        try:
            req = requests.get(page_url, timeout=10)
            req.raise_for_status()
        except requests.RequestException as error:
            print(f"Failed to scrape {page_url}: {error}")
            continue

        beautiful_soup = bs4.BeautifulSoup(req.text, "lxml")
        items = beautiful_soup.select(item_selector)

        for item in items:
            result = dict()

            for selector, field_name in zip(fields, field_names):

                element = item.select_one(selector)

                if element is None:
                    result[field_name] = None

                elif element.has_attr("title"):
                    result[field_name] = element["title"]

                else:
                    result[field_name] = element.get_text(strip=True)

            page_results.append(result)

        results[page_num] = page_results

    return results
