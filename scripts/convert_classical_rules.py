from pathlib import Path
from typing import Optional

import yaml

DOMAIN_SOURCE_DIR = Path("raw/clash/domain")
DOMAIN_OUTPUT_DIR = Path("temp/clash/domain")
IP_CIDR_SOURCE_DIR = Path("raw/clash/ip")
IP_CIDR_OUTPUT_DIR = Path("temp/clash/ip")
DOMAIN_MAP = {
    "DOMAIN": "",
    "DOMAIN-SUFFIX": "+."
}
IP_CIDR_MAP = {
    "IP-CIDR": "",
    "IP-CIDR6": ""
}


def main():
    process_dir(DOMAIN_SOURCE_DIR, DOMAIN_OUTPUT_DIR, lambda line: convert_classical(line, DOMAIN_MAP))
    process_dir(IP_CIDR_SOURCE_DIR, IP_CIDR_OUTPUT_DIR, lambda line: convert_classical(line, IP_CIDR_MAP))


def process_dir(source_path: Path, output_path: Path, fun):
    files = list(source_path.rglob("*.yaml"))
    for file in files:
        try:
            relative_path: Path = file.relative_to(source_path)
            result_path: Path = output_path / relative_path.with_suffix(".yaml")

            with open(file, "r", encoding="utf-8") as f:
                rule_lines = yaml.safe_load(f).get("payload")
            data = fun(rule_lines)
            result_path.parent.mkdir(parents=True, exist_ok=True)
            with open(result_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f)
        except Exception as e:
            print(f"转换失败 {file.name}: {e}")


def convert_classical(rule_lines: list, classical_map: dict) -> Optional[dict]:
    result: dict = {
        "payload": []
    }

    for line in rule_lines:
        if not isinstance(line, str):
            continue

        rule_type, value = parse_rule_line(line)
        if not rule_type or not value:
            continue

        if rule_type not in classical_map.keys():
            continue

        result["payload"].append(f"{classical_map[rule_type]}{value}")

    if not result.get("payload"):
        return None
    return result


def parse_rule_line(line: str) -> tuple[Optional[str], Optional[str]]:
    if "#" in line:
        line = line.split("#", 1)[0]
    parts = line.split(",")
    if len(parts) < 2:
        return None, None
    key = parts[0].strip().strip("'\"")
    value = parts[1].strip().strip("'\"")
    return key, value


if __name__ == "__main__":
    main()
