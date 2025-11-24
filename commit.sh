#!/bin/bash

# Automated git commit script for Sheltr
# Commits to login_and_register branch

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting automated git commit...${NC}"

# Ensure we're on the correct branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "login_and_register" ]; then
    echo -e "${RED}Error: Not on login_and_register branch (currently on $CURRENT_BRANCH)${NC}"
    exit 1
fi

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}No changes to commit${NC}"
    exit 0
fi

# Show status
echo -e "${YELLOW}Current status:${NC}"
git status --short

# Add all changes (respects .gitignore)
echo -e "${YELLOW}Adding changes...${NC}"
git add .

# Prompt for commit message
echo -e "${YELLOW}Enter commit message:${NC}"
read -r COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    echo -e "${RED}Error: Commit message cannot be empty${NC}"
    exit 1
fi

# Commit
echo -e "${YELLOW}Committing...${NC}"
git commit -m "$COMMIT_MSG"

# Push to remote
echo -e "${YELLOW}Pushing to origin/login_and_register...${NC}"
git push origin login_and_register

echo -e "${GREEN}Successfully committed and pushed!${NC}"
