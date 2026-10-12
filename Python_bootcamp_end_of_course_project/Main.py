from Custom_ArgumentParser import ArgumentParser
from web_scrapper import scrapper
from data_saver import save_page_data

import shlex

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()

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
        action="store_true",
        help="Show this helpful message"
    )
    
    return arg_parser

def show_header():
    console.print()
    console.print(
        Panel.fit("[bold cyan] Web Scrapper[/bold cyan]\n"
                  "[dim] Scrape and save website data[/dim]",
                  border_style="cyan"
        )
    )

def show_available_sites():
    table = Table(
        title="Available Websites",
        header_style="bold magenta"
    )

    table.add_column("#", justify="center", style="dim")
    table.add_column("Website", style="bold cyan")
    table.add_column("Pages", justify="right")
    table.add_column("URL", style="dim")

    for number, (name, website) in enumerate(WEBSITES.items(), start=1):

        table.add_row(
            str(number), 
            name, 
            str(website['number_of_pages']), 
            website["url"]
        
        )
    console.print(table)

def show_available_fields(website):
    fields = WEBSITES[website]["fields"].keys()

    console.print(
        f"\n[bold]Available fields for:"
        f"[cyan] {website}[/cyan][/bold]"
    )

    field_text = []

    for field in fields:
        field_text.append(
            f"[green]~[/green] {field}"
        )

    field_text.append(
        f"[green]~[/green] all"
    )

    console.print("     ".join(field_text))

def show_available_options():
    table = Table(
        title="Avaialble Options",
        header_style="bold blue"
    )

    table.add_column(
        "Option",
        style="bold cyan"
    )

    table.add_column(
        "Description"
    )

    table.add_column(
        "Example",
        style="green"
    )

    table.add_row(
        "--field",
        "Choose fields for scrapping",
        "--field book price"
    )

    table.add_row(
        "--pages",
        "Choose number of pages",
        "--pages 3"
    )

    table.add_row(
        "--format",
        "json / csv / txt",
        "--format csv"
    )

    table.add_row(
        "outputdir",
        "Choose output directory",
        "--outputdir results"
    )

    console.print()
    console.print(table)

    console.print(
        "\n[bold]Commands:[/bold]"
        "[green]run[/green]"
        "[cyan]show[/cyan]"
        "[yellow]reset[/yellow]"
        "[red]exit[/red]"
    )

def show_current_config(arg_parser, command_args):
    try:
        args = arg_parser.parse_args(command_args)

    except (ValueError, TypeError):
        return

    table = Table(
        title="Current configuration",
        show_header=False,
        border_style="cyan"
    )

    table.add_column(
        "Setting",
        style="cyan"
    )

    table.add_column(
        "Value",
        style="cyan"
    )

    table.add_row(
        "Website",
        args.website
    )

    table.add_row(
        "Fields",
        ", ".join(args.field)
    )

    if args.pages is None:
        pages_text += "all"
    else:
        pages_Text = str(args.pages)

    table.add_row(
        "Pages",
        pages_Text
    )

    table.add_row(
        "Format",
        args.format.upper()
    )

    table.add_row(
        "Output directory",
        args.outputdir
    )

    console.print()
    console.print(table)

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
        pages = 1

    elif args.pages <= 0:
        raise ValueError("Pages must be greater than 0")
    
    else:
        pages = min(args.pages, max_pages)

    console.print()

    console.print(
        Panel.fit(
            f"[bold]Scrapping[/bold]"
            f"[cyan]{args.website}[/cyan]\n"
            f"Pages: [green]{pages}[/green]\n"
            f"Fields: [green]{", ".join(field_names)}[/green]",
            border_style="blue"
        )
    )

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
    
    console.print()

    console.print(
        "[bold green] Scrapping completed successfully[/bold green]"
    )

    table = Table(
        title="Operation summary",
        show_header=False,
        border_style="green"
    )

    table.add_column(
        "Property",
        style="bold"
    )

    table.add_column(
        "Value",
        style="cyan"    
    )

    table.add_row(
        "Website",
        summary["website"]
    )

    table.add_row(
        "Pages scraped",
        str(summary["pages"])
    )

    table.add_row(
        "Fields",
        ", ".join(summary["fields"])
    )

    table.add_row(
        "Records",
        str(summary["records"])
    )

    table.add_row(
        "Format",
        summary["format"].upper()
    )

    console.print(table)

def print_session_summary(session_results):
    
    console.print()

    if not session_results:
        console.print(
            "[yellow]No scraping operations were performed[/yellow]"
        )
        return

    table = Table(
        title="Session Summary",
        header_style="bold magenta"
    )

    table.add_column(
        "#",
        justify="center"
    )

    table.add_column(
        "Website",
        style="cyan"
    )

    table.add_column(
        "Pages",
        justify="right"
    )

    table.add_column(
        "Records",
        justify="right"
    )

    table.add_column(
        "format"
    )

    total_records = 0

    for number, result in enumerate(session_results, start=1):
        table.add_row(
            str(number),
            result["website"],
            str(result["pages"]),
            str(result["records"]),
            result["format"].upper()
        )

        total_records += result["records"]

    console.print(table)

    console.print(
        f"[bold] total records collected: {total_records}[/bold] "
    )

def select_website():

    while True:
        user_input = Prompt.ask(
            "\n[bold cyan]Choose website [/bold cyan]"
        )

        command = user_input.lower()

        if command == "exit":
            return None

        if command in WEBSITES:
            return command

        else:
            console.print(
                "[bold red]Invalid website.[/bold red]"
                f"Choose: {", ".join(WEBSITES.keys())}"
            )


def interactive_menu(arg_parser):
    session_results = []

    while True:
        console.clear()

        show_header()
        show_available_sites()

        console.print(
            "\n[dim] Choose a website[/dim]"
        )
        selected_website = select_website()

        if selected_website is None:
            print_session_summary(
                session_results
            )

            console.print(
                "\n[bold cyan]Goodbye[/bold cyan]"
            )

            return

        command_args = [
            "--website",
            selected_website
        ]

        show_available_fields(
            selected_website
        )

        show_available_options()

        show_current_config(
            arg_parser, command_args
        )

        while True:
            user_input = input("\nscrapper> ".strip())

            if not user_input:
                continue

            command = user_input.lower()

            if command == "exit":
                print_session_summary(session_results)

                console.print(
                    "\n[bold cyan]Goodbye[/bold cyan]"
                )

                return

            if command == "run":
                try:
                    args = arg_parser.parse_args(
                        command_args
                    )

                    summary = scrape_website(args)

                    session_results.append(summary)
                    print_operation_summary(summary)

                    console.print(
                        "\n[dim]Press enter to return to website selection[/dim]"
                    )
                    input()
                    break

                except (ValueError, TypeError) as error:
                    console.print(
                        f"\n[bold red] Error: [/bold red] {error}"
                    )
                    continue

            if command == "show":
                show_current_config(
                    arg_parser, command_args
                )

                continue

            if command == "reset":

                command_args = [
                    "--website",
                    selected_website
                ]

                console.print(
                    "\n[yellow] Options reset to defaults[/yellow]"
                )

                show_current_config(
                    arg_parser, command_args
                )

                continue

            try:
                new_args = shlex.split(user_input)

            except (ValueError, TypeError) as error:

                console.print(f"[bold red]Error: [/bold red]{error}")
                continue

            if "--website" in new_args:
                console.print(
                    "[yellow]A website has already been select[/yellow]"
                )

                console.print(
                    "[dim] Finish this operation with 'run' or 'reset'[/dum]"
                )
                continue

            test_args = command_args + new_args

            try:
                parsed_test = arg_parser.parse_args(
                    test_args
                )

                if parsed_test.format not in ["json", "csv", "txt"]:
                    raise ValueError("--format must be json, csv, txt")

                if parsed_test.pages is not None and parsed_test.pages <= 0:
                    raise ValueError("--pages must be greater than 0")

                available_fields = WEBSITES[selected_website]["fields"]

                if "all" not in parsed_test.field:

                    for field in parsed_test.field:

                        if field not in available_fields:
                            raise ValueError(
                                f"Invalid field '{field}'\n"
                                f"Available fields: {", ".join(available_fields.keys())}"
                            )

            except (ValueError, TypeError) as error:
                console.print(
                    f"[bold red]Error: [/bold red] {error}"
                )
                continue

            command_args = test_args
            console.print("[green]Options updated[/green]")

            show_current_config(arg_parser, command_args)
            
def main():
   arg_parser = create_argument_parser()
   interactive_menu(arg_parser)
   
if __name__ == "__main__":
    main()