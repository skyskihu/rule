#!/bin/bash

set -e -o pipefail

src="raw/sing-box"
dst="compile/sing-box"

find "$src" -name "*.json" -type f | while read -r file; do

	result="${file/$src/$dst}"
	result="${result%.json}.srs"

	mkdir -p "$(dirname "$result")"

	sing-box rule-set compile "$file" --output "$result" || exit 1
done
