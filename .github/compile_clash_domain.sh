#!/bin/bash

set -e -o pipefail

src="raw/clash/domain"
dst="compile/clash/domain"

find "$src" -name "*.yaml" -type f | while read -r file; do

	result="${file/$src/$dst}"
	result="${result%.yaml}.mrs"

	mkdir -p "$(dirname "$result")"

	mihomo  convert-ruleset domain yaml "$file" "$result" || exit 1
done
