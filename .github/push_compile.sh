#!/bin/bash

set -e

cd compile/

git init
git checkout -b compile
git config user.name "GitHub Action"
git config user.email "action@github.com"
git add .
git commit -m "Auto-update: rules"
git remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git push -f origin compile

cd -
rm -rf compile/.git

echo "Successfully pushed compile directory to compile branch"
