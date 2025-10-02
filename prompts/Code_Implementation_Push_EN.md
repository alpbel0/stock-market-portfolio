# Code Implementation and Push Prompt (English)

## Task Description
This prompt applies analyzed Copilot suggestions to code, pushes to the current branch, and provides an English summary.

## Prompt Content

```
You are an experienced software developer. You need to apply previously analyzed Copilot suggestions to the code and push the results to the branch:

1. **Apply Suggestions**: Implement the specified "SHOULD APPLY" code changes
2. **Use GitHub CLI**: Get branch information and manage using gh commands
3. **Push Code**: Commit changes to current branch and push
4. **Provide English Summary**: Explain all changes made in English

## Steps to Follow:

### 1. Check Current Branch and PR Status
- Check PR status with `gh pr status`
- Check working directory with `git status`
- Verify which branch you're on with `git branch`
- Save any uncommitted changes if present

### 2. Apply Specified Code Changes
- Edit files for each "SHOULD APPLY" suggestion
- Apply changes carefully
- Avoid syntax errors
- Check code after each change

### 3. Test and Validation
- Run basic tests after changes (if available)
- Perform lint check (if lint configuration exists)
- Check for build errors (for compiled languages)

### 4. Git Operations
- Stage changes: `git add .`
- Write descriptive commit message
- Push to current branch: `git push`
- Check PR is updated: `gh pr view`

### 5. English Summary Report
Provide report in this format:

## 🔧 Changes Summary

**Total files changed:** [number]
**Applied suggestions count:** [number]

### File-by-File Changes:
1. **[file name]**
   - Line [line number]: [change made 1]
   - Line [line number]: [change made 2]

2. **[file name]**
   - Line [line number]: [change made]

### Technical Improvements:
- [security improvements]
- [performance improvements]  
- [code quality improvements]

### Git Status:
- Branch: [branch name]
- PR: #[PR number] - [PR title]
- Last commit: [commit hash] - [commit message]

**Status:** ✅ All changes successfully applied and pushed.
```

## Commit Message Format
```
implement: apply Copilot review suggestions

- [file]: [change summary]
- [file]: [change summary]
- Applied [number] critical improvements from code review analysis

Co-authored-by: GitHub Copilot <noreply@github.com>
```

## Important Notes
- Work on current branch, don't create new branch!
- Ensure code works after each change
- Use GitHub CLI commands to track PR status
- Roll back changes on error: `git reset --hard HEAD~1`
- Break large changes into small commits
- Always provide English summary, user must understand what was done

## Usage Instructions

1. Prepare "SHOULD APPLY" suggestions list from 2nd prompt
2. Run this prompt to apply code changes
3. Ensure GitHub CLI is installed and authenticated
4. Request English summary report at the end

## Example Usage

```bash
# GitHub CLI check
gh auth status

# Use prompt with suggestions
"Use the following prompt to apply specified changes:
[prompt content]

Suggestions to apply:
1. src/auth.js:45 - Add null check before accessing user.email
2. utils/helper.js:12 - Extract duplicate function  
3. components/Login.jsx:78 - Add error boundary

PR ID: 156

Example output format:
### File-by-File Changes:
1. **src/auth.js**
   - Line 45: Added null check before accessing user.email
   - Line 52: Added try-catch block

2. **utils/helper.js**
   - Line 12: Extracted duplicate function and moved to utils"
```

## Error Scenarios
- **Build error**: Roll back changes, fix error, try again
- **Test error**: Update related tests or revise change
- **Push error**: Run `git pull`, resolve conflicts, push again
- **PR not updated**: Check status with `gh pr view`

This prompt ensures code changes are safely applied and tracked.