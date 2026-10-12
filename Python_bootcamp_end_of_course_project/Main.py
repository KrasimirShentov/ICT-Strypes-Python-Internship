from Custom_ArgumentParser import ArgumentParser
from web_scrapper import scrapper
from data_saver import save_page_data
import shlex

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

def create_argument_parser():
    arg_parser = ArgumentParser(
        prog="Web scrapper",
        description="The user can choose between which website he wants to scrape.\n" \
        "Also he can choose the format he would like the data to be saved as.",
    )

    arg_parser.add_argument(
        "--website",
        type=str,
        default="books",
        help="Choose a website you would like to scrape."
    )

    arg_parser.add_argument(
        "--field",
        type=str,
        nargs="+",
        default=["all"],
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
    
    return arg_parser

def show_available_sites():
    print("\nAvailable website")

    for website in WEBSITES:
        print(f"    - {website}")

def show_available_fields(website):
    print(f"\nAvaialble fields for {website}")

    for field in WEBSITES[website]["fields"]:
        print(f"    - {field}")

    print("     - all")

def show_available_options():
    print("\nOther available option")
    print("  --field <field> [field ...]")
    print("  --pages <number>")
    print("  --format json/csv/txt")
    print("  --outputdir <directory>")

    print("Examples:")
    print("  --field book prie | field book")
    print("  --pages 3")
    print("  -- format csv")

    print("You can also combine them")
    print("  --field book price --pages 3 --format csv")

    print("Type 'run' when ready")
    print("Type 'exit' to exit the program")

def get_selected_Website(command_args):
    pass

def scrape_website(args):
    fields = []
    field_names = []

    if args.format not in ["json", "csv", "txt"]:
        raise TypeError("Error: --format must be json, csv, txt")

    if args.website not in WEBSITES.keys():
        raise ValueError(f"You have to choose between one of these website: {WEBSITES.keys()}")

    website = WEBSITES[args.website]

    website_fields = website["fields"]

    if "all" in args.field:

        field_names = list(website_fields.keys())
        fields = list(website_fields.values())
    else:

        for field in args.field:

            if field not in website_fields:
                raise ValueError(f"User must choose between fields that are available for the website")
            
            field_names.append(field)
            fields.append(website_fields[field])

    max_pages = website["number_of_pages"]

    if args.pages is None:
        pages = max_pages

    elif args.pages <= 0:
        raise ValueError("Pages must be greater than 0")
    
    else:
        pages = min(args.pages, max_pages)

    results = scrapper(fields, field_names, 
                    pages, website["page_format"], website["item_selector"])

    saved_files = []

    for page_num, page_data in results.items():
        file_path = save_page_data(
            page_data,
            args.format,
            args.outputdir,
            args.website,
            page_num,
            field_names
        )

        if file_path not in saved_files:
            saved_files.append(file_path)

    total_records = sum(len(page_data) for page_data in results.values())

    return {
        "website": args.website,
        "pages": len(results),
        "fields": field_names,
        "format": args.format,
        "records": total_records,
        "saved_files": saved_files
    }

def print_operation_summary(summary):
    
    print("Scrapping completed")

    print(f"Website: {summary["webiste"]}")
    print(f"Pages scrapped: {summary["pages"]}")
    print(f"Fields: {", ".join(summary["fields"])}")
    print(f"Records collected: {summary["records"]}")
    print(f"Format: {summary["format"]}")

    if summary["saved_files"]:
        print("\nFiles:")

        for file_path in summary["saved_files"]:
            print(f"  {file_path}")

def print_session_summary(session_results):
    
    if not session_results:
        print("No scrapping operations were performed")
        return

    total_records = 0

    for number, result in enumerate(session_results, start=1):

        print(f"{number}. "
              f"{result["website"]} | "
              f"{result["pages"]} | "
              f"{result["records"]} records | "
              f"{result["format"]}")

        total_records += result["records"]
    print()

    print("Total operations: "
          f"{len(session_results)}")

    print("Total records collected"
          f"{total_records}")

def interactive_menu(arg_parser):
    session_results = []

    while True:
        command_args = []

        print("Web scrapper")
        print()

        show_available_sites()
        print("\nChoose a website") 

        while True:
            user_input = input("\nscrapper> ".strip())

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print(print_session_summary(session_results))
                return

            try:
                new_args = shlex.split(user_input)

                parse_args = arg_parser.parse_args(new_args)

            except (ValueError, TypeError) as error:

                print(f"Error: {error}")
                continue

            if parse_args.website not in WEBSITES:
                print(f"Website must be one of: {", ".join(WEBSITES.keys())}")
                continue

            command_args.extend(new_args)

            selected_website = (parse_args.website)
            break

        show_available_fields(selected_website)
        show_available_options()

        print("Current arguments")
        print(" ".join(command_args))

        while True:
            user_input = input("\nscrapper> ".strip())

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print(print_session_summary(session_results))
                return

            command = user_input.lower()

            if command == "exit":
                print_session_summary(session_results)
                return

            if command == "run":
                try:
                    args = arg_parser.parse_args(command_args)
                    summary = scrape_website(args)

                    session_results.append(summary)
                    
                    print_operation_summary(summary)
    
                    break

                except (ValueError, TypeError) as error:
                    print(f"Error: {error}")
                    continue

            try:
                new_args = shlex.split(user_input)

            except ValueError as error:
                print(f"Invalid input: {error}")
                continue

            if "--website" in new_args:
                
                print("A website has already been selected")
                print("Finish the operation with 'run'")
            
                continue

            test_args = (command_args + new_args)

            try:
                arg_parser.parse_args(
                    test_args
                )
            except (ValueError, TypeError) as error:
                print(f"Error: {error}")
                continue

            command_args.extend(new_args)

            print(f"Current args: {" ".join(command_args)}")

            
            
def main():
   arg_parser = create_argument_parser()
   interactive_menu(arg_parser)
   
if __name__ == "__main__":
    main()