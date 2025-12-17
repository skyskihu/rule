#!/bin/bash

src="${1%/}"
dst="${2%/}"

[ -z "$src" -o -z "$dst" ] && echo "Usage: $0 <src> <dst>" && exit 1

find "$src" -name "*.json" -type f | while read -r file; do

	target="${file/$src/$dst}"
	target="${target%.json}.srs"

	mkdir -p "$(dirname "$target")"

	sing-box rule-set compile -o "$target" "$file" || exit 1
done
