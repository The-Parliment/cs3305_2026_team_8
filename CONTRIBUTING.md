# 🚀 Group 8 Team Guide (How we work)

To make sure we don't lose track of things over the next 7 weeks I've set up GitHub Project for the project. It keeps our GitHub board clean and makes life way easier for everyone.

## ⚠️ Watch Out! (The Board Location)
Don't look for the Project Board inside our code repo's "Projects" tab—it’s empty there. 
* Our board lives at the **"The-Parliment" Organization level**. 
* **Why:** This allows us to track everything in one big "Command Center" across multiple repos. Also, standard repo-level projects have limitations that don't easily support the custom "Epic" and "User Story" fields we need for our Agile structure.
* **Action:** Always navigate to the **Organization** page to find the board.

## 📅 1. The Game Plan (Agile stuff)
We’re working in 1-week Sprints. Everything we do needs to be an **Issue** on the board.

* **Epic:** The big goals (like "User Login" or "Final Report").
* **User Story:** A specific feature (e.g., "As a user, I want to sign up...").
* **Task:** Boring but necessary setup stuff (like "Set up folders").
* **Bug:** When something breaks.
* **Spike:** When we need a few hours to research something before we can start coding it.
* **Estimates:** Before you start, give it a **T-Shirt Size** (XS, S, M, L, XL). If it feels like an XL, we should probably break it into two smaller issues.

## 📋 2. How to use the Board
Let’s keep the board updated so we don't have to ask "What are you working on?" during standups.

You'll see I've also created a 'board' for each of us. I spotted that we need to "Individually: Create a Log book" and "update weekly" - so if we stay on top of this tool, that could be as simple as a screenshot each week.

1. **The "Current Iteration" View:** This is our main view for daily work. It only shows what we committed to for this week.
2. **Assign Yourself:** If you're doing it, put your name on it! Never work on an unassigned card (see Log book comment).
3. **Status Movement:**
    * **Todo:** Stuff waiting for this week.
    * **In Progress:** Move it here as soon as you start your branch/Draft PR.
    * **In Review:** Move it here once you’ve asked for a review.
    * **Done:** It’ll move here automatically if you link your PR correctly (see below).

## 🌿 3. Branching (Don't break the Main!)
Never push straight to `main`. Create a branch first.

**Naming your branch:** `[type]/[issue-number]-[description]`
* **story/** (Used for **User Stories**): `story/2-registration-page`
* **task/** (Used for technical setup): `task/10-seed-docs-folder`
* **bug/** (Used for **Bugs**): `bug/45-login-css`
* **spike/** (Used for research): `spike/12-db-comparison`

**Quick commands:**
```bash
git checkout main
git pull origin main
git checkout -b type/number-description
