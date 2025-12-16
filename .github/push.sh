#!/bin/bash

set -e

SOURCE_DIR="$1"      # 本地的新文件目录
BRANCH_NAME="$2"     # 目标分支
TARGET_FOLDER="$3"   # 目标分支里的文件夹名
COMMIT_MSG="$4"      # 提交信息

if [ -z "$SOURCE_DIR" ] || [ -z "$BRANCH_NAME" ] || [ -z "$TARGET_FOLDER" ]; then
    echo "Usage: $0 <source_dir> <branch_name> <target_folder_name> [commit_msg]"
    exit 1
fi

git config --global user.email "action@github.com"
git config --global user.name "GitHub Action"

# 组合仓库 URL
REPO_URL="https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"

# 定义临时克隆目录
CLONE_DIR="temp_deploy_${BRANCH_NAME}"

# 克隆目标分支
git clone --single-branch --branch "$BRANCH_NAME" "$REPO_URL" "$CLONE_DIR" || mkdir "$CLONE_DIR"
rm -rf "$CLONE_DIR/$TARGET_FOLDER"
cp -r "$SOURCE_DIR" "$CLONE_DIR/$TARGET_FOLDER"

# Git 操作
cd "$CLONE_DIR"
rm -rf .git
git init
git add .
git commit -m "${COMMIT_MSG:-Update rules}"
git push -f "$REPO_URL" HEAD:"$BRANCH_NAME"

cd ..
rm -rf "$CLONE_DIR"