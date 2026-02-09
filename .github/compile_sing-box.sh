#!/bin/bash

set -e -o pipefail

src=../../raw/sing-box
cd compile/sing-box

find "$src" -name "*.json" -type f | while read -r file; do
	sing-box rule-set compile "$file" --output "$(basename "${file%.json}.srs")" || exit 1
done
