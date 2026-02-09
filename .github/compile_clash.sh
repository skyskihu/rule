#!/bin/bash

set -e -o pipefail

src=../../raw/clash
cd compile/clash

find "$src" -name "*.yaml" -type f | while read -r file; do
	mihomo convert-ruleset "$file" --output "$(basename "${file%.json}.mrs")" || exit 1
done
