import argparse
import ipaddress
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

RULE_SET_VERSION = 3

RULE_TYPE_MAP: Dict[str, str] = {
    "DOMAIN": "domain",
    "DOMAIN-SUFFIX": "domain_suffix",
    "DOMAIN-KEYWORD": "domain_keyword",
    "DOMAIN-REGEX": "domain_regex",
    "IP-CIDR": "ip_cidr",
    "IP-CIDR6": "ip_cidr",
    "SRC-IP-CIDR": "source_ip_cidr",
    "DST-PORT": "port",
    "SRC-PORT": "source_port",
    "NETWORK": "network",
    "PROCESS-NAME": "process_name",
    "PROCESS-PATH": "process_path",
    "PROCESS-PATH-REGEX": "process_path_regex",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("source", help="源目录路径(包含 YAML 文件)")
    parser.add_argument("output", help="输出目录路径(保存 JSON 文件)")

    args = parser.parse_args()
    process_directory(args.source, args.output)


def process_directory(source_dir: str, output_dir: str) -> None:
    source_path: Path = Path(source_dir)
    output_path: Path = Path(output_dir)
    yaml_files: list[Path] = list(source_path.rglob("*.yaml"))

    if not yaml_files:
        print(f"警告：在 {source_dir} 中未找到 YAML 文件")
        return
    else:
        print(f"找到 {len(yaml_files)} 个 YAML 文件")

    success_count: int = 0
    error_count: int = 0

    for yaml_file in yaml_files:
        try:
            relative_path: Path = yaml_file.relative_to(source_path)
            json_file: Path = output_path / relative_path.with_suffix(".json")
            json_file.parent.mkdir(parents=True, exist_ok=True)

            json_data = convert_yaml_to_json(yaml_file)

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            success_count += 1

        except Exception as e:
            print(f"转换失败 {yaml_file.name}: {e}")
            error_count += 1

    print(f"转换完成：成功 {success_count} 个，失败 {error_count} 个")


def convert_yaml_to_json(yaml_path: Path) -> Dict[str, Any]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

    rules_map: Dict[str, list[Any]] = defaultdict(list)

    for line in yaml_data.get("payload"):
        if not isinstance(line, str):
            continue

        rule_type, value = parse_rule_line(line)

        if not rule_type or not value:
            continue

        if rule_type not in RULE_TYPE_MAP:
            continue

        if not verify(rule_type, value):
            continue

        key = RULE_TYPE_MAP[rule_type]

        if rule_type in ["DST-PORT", "SRC-PORT"]:
            value = int(value)
        elif rule_type == "NETWORK":
            value = value.lower()

        rules_map[key].append(value)

    json_rules: list[dict[str, list[Any]]] = [{key: values} for key, values in rules_map.items()]
    json_data: Dict[str, Any] = {
        "version": RULE_SET_VERSION,
        "rules": json_rules
    }

    return json_data


def parse_rule_line(line: str) -> tuple[Optional[str], Optional[str]]:
    # 移除行内注释
    if "#" in line:
        line = line.split("#", 1)[0]

    # 按逗号分割字符串
    parts = line.split(",")
    if len(parts) < 2:
        return None, None

    # 提取前两个部分: 类型和值
    rule_type = parts[0].strip().strip("'\"")
    rule_value = parts[1].strip().strip("'\"")

    return rule_type, rule_value


def verify(rule_type: str, value: str) -> bool:
    if rule_type in ["IP-CIDR", "IP-CIDR6", "SRC-IP-CIDR"]:
        return validate_ip_cidr(value)
    elif rule_type in ["DST-PORT", "SRC-PORT"]:
        return validate_port(value)
    elif rule_type == "NETWORK":
        return validate_network(value)
    elif rule_type == "DOMAIN-REGEX":
        return validate_regex(value)
    elif rule_type in ["DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"]:
        return validate_domain(value)
    return True


def validate_ip_cidr(value: str) -> bool:
    try:
        ipaddress.ip_network(value, strict=False)
        return True
    except ValueError:
        return False


def validate_port(value: str) -> bool:
    try:
        port = int(value)
        return 1 <= port <= 65535
    except ValueError:
        return False


def validate_network(value: str) -> bool:
    return value.lower() in ["tcp", "udp"]


def validate_regex(value: str) -> bool:
    try:
        re.compile(value)

        # 检查 Golang RE2 不支持的特性
        unsupported_patterns = [
            r"\1", r"\2", r"\3", r"\4", r"\5", r"\6", r"\7", r"\8", r"\9",
            r"(?<", r"(?<=", r"(?<!",
            r"(?(", r"(?P=",
        ]

        for pattern in unsupported_patterns:
            if pattern in value:
                return False

        if re.search(r"\\[1-9]", value):
            return False

        return True
    except re.error:
        return False


def validate_domain(value: str) -> bool:
    if not value or len(value) > 253:
        return False
    return True


if __name__ == "__main__":
    main()
