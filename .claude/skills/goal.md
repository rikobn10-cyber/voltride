---
name: goal
description: Define the single specific goal for the current Claude Code session
user-invocable: true
argument-hint: ""
version: "1.0.0"
---

# Goal Skill

## Purpose
This skill helps establish and document the primary focus for a Claude Code session, ensuring both Claude and the user stay aligned on objectives.

## Usage
Invoke this skill at the start of a session or when the goal needs to be reassessed:
```
/goal
```

## Workflow

### Step 1: Ask for the Specific Goal
Ask the user:
> What is the single specific goal you want me to accomplish in this session? Please be as focused and specific as possible.

### Step 2: Receive and Confirm
Wait for the user's response, then confirm understanding:
> I understand the goal is: **[user's goal]**. Is this correct?

### Step 3: Create SESSION_GOAL.md
Create a file named `SESSION_GOAL.md` in the repository root with the following structure:

```markdown
# Session Goal

**Date:** YYYY-MM-DD
**Goal:** [The specific goal from the user]

## Context
[Optional: brief context about why this goal matters or any constraints]

## Success Criteria
- [ ] Specific, measurable outcome
- [ ] Clear definition of "done"

## Constraints
- Any file protection requirements
- No modifications to specific files
- Deployment restrictions
- etc.
```

### Step 4: Remind User of Focus
After creating the file, inform the user:
> Your session goal has been saved to `SESSION_GOAL.md`. This goal is your primary focus throughout this session. All work should progress toward this objective.

## Important Rules
1. **Single Focus:** Only ONE session goal at a time
2. **Specificity:** The goal should be actionable, not vague
3. **Written Down:** Always create the SESSION_GOAL.md file
4. **Reference:** Refer back to this goal when work diverges
5. **Update:** If scope changes, update SESSION_GOAL.md with user approval

## Example Prompts for Goal Setting

**Bad (too vague):**
- "Help me with the project"
- "Make the site better"

**Good (specific):**
- "Translate the Arabic article blog/charger-safety.html to English and create en/blog/charger-safety.html"
- "Fix the broken affiliate link in article-10.html"
- "Add three missing hreflang entries to sitemap.xml for the French articles"

## File Output
Always output the SESSION_GOAL.md file in the repository root directory.