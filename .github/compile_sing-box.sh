#!/bin/bash

set -e -o pipefail

src="${1%/}"
dst="${2%/}"

find "$src" -name "*.json" -type f | while read -r file; do

	target="${file/$src/$dst}"
	target="${target%.json}.srs"

	mkdir -p "$(dirname "$target")"

	sing-box rule-set compile "$file" --output "$target" || exit 1
done
