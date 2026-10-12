import json, os, csv
from datetime import datetime
import hashlib

FORMATS = ["json", "csv", "txt"]

def get_data_hash(data):
    normalized_data = json.dumps(
        data, sort_keys=True, ensure_ascii=False
    )

    return hashlib.sha256(
        normalized_data.encode("utf-8")
    ).hexdigest()

def get_page_directory(output_dir, website, page):
    return os.path.join(
        output_dir, 
        f"{website}_scrapped", 
        f"page_{page}"
    )

def get_file_path(page_directory, website, page, file_format):
    # time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_name = f"{website}_{page}.{file_format}"

    return os.path.join(
        page_directory,
        file_name,
    )

def write_meta_data(page_directory, data_hash, field_names, records):
    medadata_path = os.path.join(
            page_directory,
            "_metadata.json"
        )

    metadata = {
        "hash_content": data_hash,
        "fields": field_names,
        "records": records
    }

    with open(medadata_path, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False
        )

def read_meta_data(page_directory):
    medadata_path = os.path.join(
        page_directory,
        "_metadata.json"
    )

    if not os.path.exists(medadata_path):
        return None

    try:
        with open(medadata_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except(OSError, json.JSONDecodeError):
        return None

def read_stored_data(page_directory):
    data_path = os.path.join(
        page_directory, "_data.json"
    )

    if not os.path.exists(data_path):
        return None

    try:
        with open(data_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError):
        return None

    
def write_stored_data(page_directory, data):
    data_path = os.path.join(
        page_directory, "_data.json"
    )

    with open(data_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

def merge_data(old_data, new_data):
    if len(old_data) != len(new_data):
        return None

    merged_data = []

    for i in range(len(old_data)):
        merged_item = old_data[i].copy()
        merged_item.update(new_data[i])

        merged_data.append(merged_item)

    return merged_data 

def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data, file,
            indent=4,
            ensure_ascii=False
        )

def save_csv(data, file_path, field_names):

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data)

def save_txt(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        for item in data:

            for key, value in item.items():
                file.write(f"{key}: {value}\n")

            file.write("\n")

def save_format(data, file_format, page_directory, website, page, field_names):
    file_path = get_file_path(
        page_directory,
        website,
        page,
        file_format,
    )

    if file_format == "json":
        save_json(data, file_path)

    elif file_format =="csv":
        save_csv(data, file_path, field_names)

    elif file_format == "txt":
        save_txt(data, file_path)

    return file_path

def rewrite_existing_formats(data, page_directory, website, page, requested_format, field_names):
    formats_to_rewrite = []

    for file_format in FORMATS:
        file_path = get_file_path(
            page_directory,
            website,
            page,
            file_format
        )

        if os.path.exists(file_path):
            formats_to_rewrite.append(file_format)
    
    if requested_format not in formats_to_rewrite:
        formats_to_rewrite.append(requested_format)

    for file_format in formats_to_rewrite:
        save_format(
            data,
            file_format,
            page_directory,
            website,
            page,
            field_names
        )

def save_page_data(data, file_format, output_dir, website, page, field_names):
    if not data:
        print(f"Page {page} doesnt contain any data")

    page_directory = get_page_directory(
        output_dir, website, page
    )

    os.makedirs(page_directory, exist_ok=True)

    new_hash = get_data_hash(data)
    metadata = read_meta_data(page_directory)

    requested_file = get_file_path(
        page_directory,
        website,
        page,
        file_format
    )

    if metadata is None:
        file_path = save_format(
            data,
            file_format,
            page_directory,
            website,
            page,
            field_names
        )

        write_stored_data(
            page_directory,
            data
        )

        write_meta_data(
            page_directory, 
            new_hash, 
            field_names, 
            len(data)
        )

        print(f"Page {page} saved successfully")
        print(f"Saved to: {file_path}")

        return file_path

    old_hash = metadata.get("hash_content")
    old_fields = metadata.get("fields", [])
    old_data = read_stored_data(page_directory)

    if old_data is None:
        print(f"Stored data for page {page} could not be loaded")
        return None

    if set(old_fields) != set(field_names):
        print(f"\nPage {page} has already been scrapped with different fields")
        print(f"Previously saved fields: {', '.join(old_fields)}")
        print(f"Current fields: {", ".join(field_names)}")

        answer = input("Would you like to merge these fields with the stored data [y/n]: ").lower()
        
        if answer != "y":
            print("Existing data was not changed")
            return None

        merged_data = merge_data(old_data, data)

        if merged_data is None:
            print("The number of records on the page has changed")
            print("The old and new data connot be merged safely")

            return None

        combined_fields = list(
            dict.fromkeys(
                old_fields + field_names
            )
        )

        rewrite_existing_formats(
            merged_data,
            page_directory,
            website,
            page,
            file_format,
            combined_fields
        )

        write_stored_data(
            page_directory,
            merged_data
        )

        merged_hash = get_data_hash(
            merged_data
        )
    
        write_meta_data(
            page_directory,
            merged_hash,
            combined_fields,
            len(merged_data)
        )

        print(f"Page {page} has been updated with the new fields")
        
        return requested_file

    if old_hash == new_hash:
        if os.path.exists(requested_file):
            print(f"Page {page} has already been scrapped\n and the content has not changed!")
            print(f"You can find it at: {requested_file}")

            return requested_file

        file_path = save_format(
            data,
            file_format,
            page_directory,
            website,
            page,
            field_names
        )

        print(f"Page {page} was already scrapped\nThe content has not changed")
        print(f"The {file_format.upper()} version\nwas created at: {file_path}")

        return file_path

    print(f"\nPage {page} was scrapped before.")
    print("The content of the page has changed")

    answer = input("Would you like to replace the stored page with the new content [y/n]: ").lower()

    if answer != "y":
        print("Existing data was not changed")
        return None

    rewrite_existing_formats(
        data,
        page_directory,
        website,
        page,
        file_format,
        field_names
    )

    write_stored_data(
        page_directory,
        data
    )

    write_meta_data(
        page_directory,
        new_hash,
        field_names,
        len(data)
    )

    print(f"Page {page} was updated with the new content")

    return requested_file