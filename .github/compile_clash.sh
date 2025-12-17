#!/bin/bash

set -e -o pipefail

src="${1%/}"
dst="${2%/}"

find "$src" -name "*.yaml" -type f | while read -r file; do

	target="${file/$src/$dst}"
	target="${target%.yaml}.mrs"

	mkdir -p "$(dirname "$target")"

	mihomo convert-ruleset "$file" "$target" || exit 1
done
