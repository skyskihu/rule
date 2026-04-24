from pathlib import Path
from typing import Optional

import yaml

SOURCE_DIR = "source"
IP_CIDR_OUTPUT_DIR = "raw/clash/ipcidr"
DOMAIN_OUTPUT_DIR = "raw/clash/domain"

IP_CIDR_KEY = ["IP-CIDR", "IP-CIDR6"]
DOMAIN_MAP = {
    "DOMAIN": "",
    "DOMAIN-SUFFIX": "+."
}


def main():
    source_path: Path = Path(SOURCE_DIR)
    domain_output_path: Path = Path(DOMAIN_OUTPUT_DIR)
    ip_cidr_output_path: Path = Path(IP_CIDR_OUTPUT_DIR)

    yaml_files: list[Path] = list(source_path.rglob("*.yaml"))
    print(f"找到 {len(yaml_files)} 个 YAML 文件")

    for yaml_file in yaml_files:
        try:
            relative_path: Path = yaml_file.relative_to(source_path)
            domain_path: Path = domain_output_path / relative_path.with_suffix(".yaml")
            ip_cidr_path: Path = ip_cidr_output_path / relative_path.with_suffix(".yaml")

            with open(yaml_file, "r", encoding="utf-8") as f:
                yaml_data: dict = yaml.safe_load(f)
                if not isinstance(yaml_data, dict) or not yaml_data:
                    continue

                rule_lines: list[str] = yaml_data.get("payload")
                if not isinstance(rule_lines, list) or not yaml_data:
                    continue

                domain_data = process_domain(rule_lines)
                ip_cidr_data = process_ip_cidr(rule_lines)

            if domain_data:
                domain_path.parent.mkdir(parents=True, exist_ok=True)
                with open(domain_path, "w", encoding="utf-8") as f:
                    yaml.dump(domain_data, f)

            if ip_cidr_data:
                ip_cidr_path.parent.mkdir(parents=True, exist_ok=True)
                with open(ip_cidr_path, "w", encoding="utf-8") as f:
                    yaml.dump(ip_cidr_data, f)

        except Exception as e:
            print(f"转换失败 {yaml_file.name}: {e}")


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
    # 移除行内注释
    if "#" in line:
        line = line.split("#", 1)[0]

    # 按逗号分割字符串
    parts = line.split(",")
    if len(parts) < 2:
        return None, None

    # 提取 key and value
    key = parts[0].strip().strip("'\"")
    value = parts[1].strip().strip("'\"")

    return key, value


if __name__ == "__main__":
    main()
