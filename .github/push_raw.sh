#!/bin/bash

set -e -o pipefail

cd raw

git init
git checkout -b raw
git config user.name "GitHub Action"
git config user.email "action@github.com"
git add .
git commit -m "Auto-update: rules"
git remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git push -f origin raw
