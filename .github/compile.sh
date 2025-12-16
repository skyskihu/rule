#!/bin/bash

SOURCE_DIR="$1" # 源目录
OUTPUT_DIR="$2" # 目标目录

if [ -z "$SOURCE_DIR" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <source_json_dir> <output_srs_dir>"
    exit 1
fi

# 检查 sing-box 是否安装
if ! command -v sing-box &> /dev/null; then
    echo "Error: sing-box command not found"
    exit 1
fi

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

echo "Starting compilation from $SOURCE_DIR to $OUTPUT_DIR..."

# 查找所有 json 文件
find "$SOURCE_DIR" -name "*.json" -type f | while IFS= read -r file; do
    # 计算相对路径
    clean_source=${SOURCE_DIR%/}
    relative_path="${file#$clean_source/}"
    
    # 获取目录结构和文件名
    file_dir=$(dirname "$relative_path")
    filename=$(basename "$file" .json)
    
    # 构建目标文件路径
    if [ "$file_dir" != "." ]; then
        mkdir -p "$OUTPUT_DIR/$file_dir"
        target_file="$OUTPUT_DIR/$file_dir/$filename.srs"
    else
        target_file="$OUTPUT_DIR/$filename.srs"
    fi
    
    # 编译
    sing-box rule-set compile --output "$target_file" "$file" || exit 1
done