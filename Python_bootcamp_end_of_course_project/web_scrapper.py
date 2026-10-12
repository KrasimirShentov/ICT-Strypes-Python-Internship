import requests
import bs4

def scrapper(fields, field_names, page, url_format, item_selector):
    """
    Scrape one or more pages from a website.

    For each page, matching items are selected using the provided
    item selector. Requested fields are extracted from every item
    and grouped by page number.
    """
    
    results = dict()

    for page_num in range(1, page + 1):
        page_url = url_format.format(page_num)
        page_results = []
 
        try:
            req = requests.get(page_url, timeout=10)
            req.encoding = "utf-8"
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
                    text = element.get_text(strip=True)

                    if text:
                        result[field_name] = text
                    else:
                        result[field_name] = None


            page_results.append(result)

        results[page_num] = page_results

    return results
