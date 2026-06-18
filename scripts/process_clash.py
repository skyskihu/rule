from pathlib import Path
from typing import Optional

import yaml

DOMAIN_SOURCE_DIR = "raw/clash/domain"
DOMAIN_OUTPUT_DIR = "temp/clash/domain"
IP_CIDR_SOURCE_DIR = "raw/clash/ip"
IP_CIDR_OUTPUT_DIR = "temp/clash/ip"

IP_CIDR_KEY = ["IP-CIDR", "IP-CIDR6"]
DOMAIN_MAP = {
    "DOMAIN": "",
    "DOMAIN-SUFFIX": "+."
}


def main():
    domain_path: Path = Path(DOMAIN_SOURCE_DIR)
    ip_cidr_path: Path = Path(IP_CIDR_SOURCE_DIR)
    domain_output_path: Path = Path(DOMAIN_OUTPUT_DIR)
    ip_cidr_output_path: Path = Path(IP_CIDR_OUTPUT_DIR)

    process_dir(domain_path, domain_output_path, process_domain)
    process_dir(ip_cidr_path, ip_cidr_output_path, process_ip_cidr)


def process_dir(source_path: Path, output_path: Path, fun):
    files = list(source_path.rglob("*.yaml"))
    print(f"找到 {len(files)} 个 domain 文件")
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


def process_domain(rule_lines: list) -> Optional[dict]:
    result: dict = {
        "payload": []
    }

    for line in rule_lines:
        if not isinstance(line, str):
            continue

        rule_type, value = parse_rule_line(line)
        if not rule_type or not value:
            continue

        if rule_type not in DOMAIN_MAP.keys():
            continue

        result["payload"].append(f"{DOMAIN_MAP[rule_type]}{value}")

    if not result.get("payload"):
        return None
    return result


def process_ip_cidr(rule_lines: list) -> Optional[dict]:
    result: dict = {
        "payload": []
    }

    for line in rule_lines:
        if not isinstance(line, str):
            continue

        rule_type, value = parse_rule_line(line)
        if not rule_type or not value:
            continue

        if rule_type not in IP_CIDR_KEY:
            continue

        result["payload"].append(value)

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
