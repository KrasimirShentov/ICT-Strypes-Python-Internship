from Custom_ArgumentParser import ArgumentParser
from web_scrapper import scrapper
from data_saver import save_data

WEBSITES = {
    "quotes": {
         "url": "https://quotes.toscrape.com",
         "page_format": "https://quotes.toscrape.com/page/{}/",
         "number_of_pages": 10,

         "item_selector": ".quote",
         "fields":{
             "quote": ".text",
             "author": ".author",
             "tags": ".tags"
         }
    },
    "books": {
        "url": "https://books.toscrape.com",
        "page_format": "https://books.toscrape.com/catalogue/page-{}.html",
        "number_of_pages": 50,

        "item_selector": "article.product_pod",
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
    field_names = []
    
    arg_parser = ArgumentParser(
        prog="Web scrapper",
        description="The user can choose between which website he wants to scrape.\n" \
        "Also he can choose the format he would like the data to be saved as.",
    )

    arg_parser.add_argument(
        "--website",
        type=str,
        default="https://books.toscrape.com",
        help="Choose a website you would like to scrape."
    )

    arg_parser.add_argument(
        "--field",
        type=str,
        nargs="+",
        default="all",
        help="User can choose which fields he would like to scrape."
    )

    arg_parser.add_argument(
        "--pages",
        type=int,
        default=None,
        help="User can choose from how many web pages he want to scrape."
    )

    arg_parser.add_argument(
        "--format",
        type=str,
        default="json",
        help="Output format: json, csv, txt"
    )

    arg_parser.add_argument(
        "--outputdir",
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

    # manual_test = ["--website", "books", "--pages", "2", "--field", "book"]
    # args = arg_parser.parse_args(manual_test)
    args = arg_parser.parse_args()
    print(args)

    if args.format not in ["json", "csv", "txt"]:
        raise TypeError("Error: --format must be json, csv, txt")

    if args.website not in WEBSITES.keys():
        raise ValueError(f"You have to choose between one of these website: {WEBSITES.keys()}")

    url = WEBSITES[args.website]["url"]
    website_fields = WEBSITES[args.website]["fields"]

    if args.field == "all":
        field_names = list(website_fields.keys())
        fields = list(website_fields.values())
        print(fields)
    else:
        for field in args.field:
            if field not in website_fields:
                raise ValueError(f"User must choose between fields that are available for the website")
            
            field_names.append(field)
            fields.append(website_fields[field])
            print(fields, "\n", field_names)

    max_pages = WEBSITES[args.website]["number_of_pages"]

    if args.pages is None:
        pages = max_pages
    elif args.pages <= 0:
        raise ValueError("Pages must be greater than 0")
    else:
        pages = min(args.pages, max_pages)

    print(pages)
    print(WEBSITES[args.website]["number_of_pages"])

    page_url_format = WEBSITES[args.website]["page_format"]
    urls.append(url)
    number_of_pages = WEBSITES[args.website]["number_of_pages"]
    print(number_of_pages)
    item_selector = WEBSITES[args.website]["item_selector"]

    results = scrapper(fields, field_names, 
                       pages, page_url_format, item_selector)

    file_path = save_data(
        results,
        args.format,
        args.outputdir,
        args.website
    )

    if file_path:
        print("Successful scrapping")
    
if __name__ == "__main__":
    main()