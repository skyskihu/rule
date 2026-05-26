import shutil
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "source"
CLASH_CLASSICAL_DIR = BASE_DIR / "raw/clash"


def main():
    copy_files(SOURCE_DIR, CLASH_CLASSICAL_DIR)
    process_dir(CLASH_CLASSICAL_DIR)


def copy_files(src: Path, dst: Path):
    shutil.copytree(src, dst, dirs_exist_ok=True)


def process_dir(src: Path):
    if src.is_file():
        return

    flag = True
    iterators = src.iterdir()
    for iterator in iterators:
        if iterator.is_dir():
            flag = False
            process_dir(iterator)
    if flag:
        merge_rules(src)


def merge_rules(src: Path):
    files = src.glob("*.yaml")
    output_file = src.parent / (src.stem + "/all.yaml")
    rule_line = []
    for file in files:
        yaml_data = yaml.safe_load(file.read_text()).get("payload")
        if isinstance(yaml_data, list) and yaml_data:
            rule_line.extend(yaml_data)
    with open(output_file, "w") as f:
        yaml.dump({"payload": rule_line}, f)


if __name__ == "__main__":
    main()
