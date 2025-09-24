#!/bin/bash

# Quick git push script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Git Push to GitHub ===${NC}"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    git remote add origin https://github.com/quake0day/Dodrio.git
fi

# Add all changes
echo -e "${YELLOW}Adding changes...${NC}"
git add .

# Get commit message
if [ -z "$1" ]; then
    echo -e "${YELLOW}Enter commit message:${NC}"
    read commit_message
else
    commit_message="$*"
fi

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git commit -m "$commit_message"

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push origin main || git push origin master || git push -u origin main

echo -e "${GREEN}✓ Push complete!${NC}"
echo -e "${GREEN}GitHub Actions will now automatically deploy to your server.${NC}"