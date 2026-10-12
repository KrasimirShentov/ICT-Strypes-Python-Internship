import json, os, csv
from datetime import datetime

def save_data(data, file_format, output_dir, website):
    if not data:
        print("There is not available data")
        return None

    os.makedirs(output_dir, exist_ok=True)

    time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_name = f"{website}_{time_stamp}.{file_format}"
    file_path = os.path.join(output_dir, file_name)

    try:
        if file_format == "json":
            save_json(data, file_path)
        elif file_format =="csv":
            save_csv(data, file_path)
        elif file_format == "txt":
            save_txt(data, file_path)
    except OSError as error:
        print(f"Failed to save file: {error}")
        return None

    return file_path

def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data, file,
            indent=4,
            ensure_ascii=True
        )

def save_csv(data, file_path):
    field_names = data[0].keys()

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
