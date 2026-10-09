from Custom_ArgumentParser import ArgumentParser
from web_scrapper import scrapper
import sys

WEBSITES = {
    "quotes": {
         "url": "https://quotes.toscrape.com",
         "page_format": "https://quotes.toscrape.com/page/1/",
         "number_of_pages": 11,
         "fields":{
             "quote": ".text",
             "author": ".author",
             "tags": ".tags"
         }
    },
    "books": {
        "url": "https://books.toscrape.com",
        "page_format": "https://books.toscrape.com/catalogue/page-1",
        "number_of_pages": 51,
        "fields":{
            "book": "h3 a",
            "price": ".price_color",
            "instock": ".instock.availability"
        }
    },
}

def main():
    urls = []
    fields = []
    
    arg_parser = ArgumentParser(
        prog="Web scrapper",
        description="The user can choose between which website he wants to scrape.\n" \
        "Also he can choose the format he would like the data to be saved as.",
    )

    arg_parser.add_argument(
        "--website",
        type=str,
        default="https://books.toscrape.com",
        help="Choose a website you would like to scrape"
    )

    arg_parser.add_argument(
        "--field",
        type=str,
        nargs="+",
        default="all",
        help="User can choose which fields he would like to scrape"
    )

    arg_parser.add_argument(
        "--format",
        type=str,
        default="json",
        help="Output format: json, csv, txt"
    )

    arg_parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Choose where scrapped file will be saved"
    )

    arg_parser.add_argument(
        "-h", "--help",
        type=str,
        action="store_true",
        help="Show this helpful message"
    )

    args = arg_parser.parse_args(["--website", "quotes", "--field", "quote"])
    print(args)

    if args.format not in ["json", "csv", "txt"]:
        raise TypeError("Error: --format must be json, csv, txt")

    if args.website not in WEBSITES.keys():
        raise ValueError(f"You have to choose between one of these website: {WEBSITES.keys()}")

    url = WEBSITES[args.website]["url"]
    website_fields = WEBSITES[args.website]["fields"]

    if args.field == "all":
        fields = website_fields
    else:
        for field in args.field:
            if field not in website_fields:
                raise ValueError(f"User must choose between fields that are available for the website")
            
            fields.append(website_fields[field])

    urls.append(url)
    number_of_pages = WEBSITES[args.website]["number_of_pages"]
    print(number_of_pages)

    for page in range(1, number_of_pages):
        scrapper(urls, fields, page)
    
if __name__ == "__main__":
    main()