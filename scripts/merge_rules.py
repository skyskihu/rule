import shutil
from pathlib import Path

import yaml

SOURCE_DIR = Path("source/")
OUTPUT_DIR = Path("temp/clash")
EXCLUDE_DIR = ["other", "ip"]


def main():
    shutil.copytree(SOURCE_DIR, OUTPUT_DIR, dirs_exist_ok=True)
    process_dir(OUTPUT_DIR)


def process_dir(src: Path):
    if src.is_file():
        return

    iterators = src.iterdir()
    for iterator in iterators:
        if iterator.is_dir() and iterator.name.lower() not in EXCLUDE_DIR:
            process_dir(iterator)
    merge_rules(src)


def merge_rules(src: Path):
    files = src.glob("*.yaml")
    output_file = src.parent / (src.stem + "/all.yaml")
    rule_line = []
    for file in files:
        yaml_data = yaml.safe_load(file.read_text()).get("payload")
        if isinstance(yaml_data, list) and yaml_data:
            rule_line.extend(yaml_data)
    if not rule_line:
        return
    with open(output_file, "w") as f:
        yaml.dump({"payload": rule_line}, f)


if __name__ == "__main__":
    main()
