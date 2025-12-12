#!/bin/bash

# Git push script for Sheltr repository via SSH

REPO_SSH="git@github.com:rammy427/Sheltr.git"
USER_EMAIL="ian.perez5@upr.edu"
SSH_KEY="$HOME/.ssh/id_ed25519"

# Change to script directory
cd "$(dirname "$0")"

# Configure git to use the SSH key
export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes"

# Initialize git repo if not already initialized
if [ ! -d ".git" ]; then
    git init
fi

# Ensure git user email is set for this repo
git config user.email "$USER_EMAIL"

# Prompt for branch name
read -p "Enter branch name: " BRANCH_NAME

if [ -z "$BRANCH_NAME" ]; then
    echo "Error: Branch name cannot be empty."
    exit 1
fi

# Prompt for commit message
read -p "Enter commit message: " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    echo "Error: Commit message cannot be empty."
    exit 1
fi

# Check if remote 'origin' exists and update it, or add it
if git remote get-url origin &>/dev/null; then
    git remote set-url origin "$REPO_SSH"
else
    git remote add origin "$REPO_SSH"
fi

# Stage all changes
git add .

# Commit with the provided message
git commit -m "$COMMIT_MSG"

# Create/switch to the branch
git checkout -B "$BRANCH_NAME"

# Push to the specified branch
git push -u origin "$BRANCH_NAME"

echo "Pushed to branch '$BRANCH_NAME' successfully."
