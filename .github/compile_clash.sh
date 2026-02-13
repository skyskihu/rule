#!/bin/bash

set -e -o pipefail

src="raw/clash"
dst="compile/clash"

find "$src" -name "*.yaml" -type f | while read -r file; do

	target="${file/$src/$dst}"
	target="${target%.yaml}.mrs"

	mkdir -p "$(dirname "$target")"

	mihomo convert-ruleset "$file" "$target" || exit 1
done
