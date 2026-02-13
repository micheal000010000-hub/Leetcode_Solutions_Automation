# 🚀 LeetCode AutoSync with Gemini 2.5 Flash

Automate your LeetCode workflow like a professional.

This tool helps you:

- ✅ Add new LeetCode solutions locally (organized by difficulty)
- ✅ Automatically update your main LeetCode repository README (sorted numerically)
- ✅ Generate a fully structured LeetCode Solution Post using **Gemini 2.5 Flash**
- ✅ Instantly copy-paste AI-generated content into LeetCode “Solutions” section
- ✅ Push changes to GitHub with a formatted date-based commit message
- ✅ Keep generated solution posts separate and excluded from Git tracking

---

# ✨ Why This Exists

When practicing LeetCode daily, the repetitive tasks become exhausting:

- Creating new files manually
- Adding headers
- Updating README
- Sorting entries
- Writing solution explanations
- Formatting markdown properly
- Committing and pushing to GitHub

This tool automates all of it.

It lets you focus on solving problems — not managing files.

---

# 🧠 What This Tool Does

When you run:

```
python autosync.py
```

You get two options:

```
1 → Add new solution locally + Generate AI solution post
2 → Push existing changes to GitHub
```

---

## 🔹 Option 1 — Add New Solution + Generate AI Post

You provide:

- Problem number
- Problem name
- Difficulty (easy / medium / hard)
- Problem link
- Your Python solution

The tool then:

### 1️⃣ Creates the solution file

Inside your LeetCode repository:

```
easy/
medium/
hard/
```

With proper formatting:

```python
"""
LeetCode 506_Relative Ranks
Difficulty: Easy
Link: https://leetcode.com/...
"""
```

---

### 2️⃣ Updates README.md

- Inserts the solution under the correct difficulty section
- Sorts entries numerically (e.g., 1, 2, 506)
- Prevents duplicates

---

### 3️⃣ Calls Gemini 2.5 Flash

It generates a structured solution post including:

- A professional, descriptive title  
  (e.g., "O(n) HashMap-Based Python Solution | Clean Approach")
- ## Intuition
- ## Approach
- ## Time Complexity
- ## Space Complexity
- ## Code (formatted with ```python3)

You can directly copy-paste it into LeetCode’s **Solutions** section.

---

### 4️⃣ Saves AI Output Locally

Inside:

```
leetcode_autosync/
└── copy_paste_solution/
```

This folder:

- Is automatically cleared before every run
- Always contains only ONE fresh structured solution
- Is ignored by Git

---

## 🔹 Option 2 — Push to GitHub

Runs:

```
git add .
git commit -m "commit_DD_MM_YYYY"
git push -f
```

Using today's date automatically.

---

# 🤖 AI Model Used

This project uses:

## Gemini 2.5 Flash

Model: `gemini-2.5-flash`  
SDK: `google-genai`

Why Gemini 2.5 Flash?

- Fast response time
- High-quality technical writing
- Excellent structured markdown generation
- Strong reasoning for time & space complexity detection

---

# 📁 Project Structure

```
leetcode_autosync/
│
├── autosync.py              # Main CLI entry point
├── config.py                # Loads environment variables
├── repo_manager.py          # File creation + README updates
├── git_manager.py           # Git automation
├── llm_generator.py         # Gemini 2.5 Flash integration
│
├── copy_paste_solution/     # Auto-cleared AI output folder (ignored by git)
│
├── .env                     # Environment variables (NOT committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 📂 Required Structure of Your LeetCode Repository

Your main LeetCode repo must look like this:

```
LeetCode Solutions/
│
├── easy/
├── medium/
├── hard/
└── README.md
```

Your README must contain sections:

```
## Easy
## Medium
## Hard
```

The tool will:

- Insert new entries
- Keep them sorted
- Avoid duplicates

---

# 🔐 .env Configuration

Create a `.env` file inside `leetcode_autosync/`:

```
LEETCODE_REPO_PATH=ABSOLUTE_PATH_TO_YOUR_LEETCODE_REPO
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Example (Windows):

```
LEETCODE_REPO_PATH=C:/Users/YourName/Documents/LeetCode Solutions
```

Example (Mac/Linux):

```
LEETCODE_REPO_PATH=/Users/yourname/Documents/LeetCode Solutions
```

---

# 📦 requirements.txt

```
python-dotenv
google-genai
```

Install:

```
pip install -r requirements.txt
```

---

# 🚫 .gitignore

```
.env
__pycache__/
*.pyc
copy_paste_solution/
```

---

# 🛠 How It Works (High-Level Architecture)

```
You
  ↓
autosync.py (CLI)
  ↓
repo_manager.py
  ↓
Updates LeetCode Repo
  ↓
llm_generator.py
  ↓
Gemini 2.5 Flash
  ↓
Structured Markdown Output
  ↓
Saved in copy_paste_solution/
```

Clean separation of responsibilities.

---

# 🎯 Who Is This For?

- Students practicing LeetCode daily
- Developers building public GitHub consistency
- Anyone wanting automated structured solution posts
- Learners who want to focus on problem-solving, not formatting

---

# 💡 Why This Is Powerful

You now have:

- Repository automation
- AI-assisted explanation writing
- Proper markdown formatting
- Organized solution tracking
- One-command GitHub publishing
- A reproducible workflow system

This is not just automation.

It is workflow engineering.

---

# 🧩 Future Improvements (Optional Ideas)

- Auto-copy generated markdown to clipboard
- Auto-open LeetCode submission page
- Auto-update “Last Updated” timestamp in README
- Auto-detect duplicate problem entries
- Add colored CLI output
- Add logging system
- Add statistics dashboard

---

# 🤝 Contributions

Contributions are welcome!

If you'd like to:

- Improve prompt quality
- Enhance formatting
- Add model selection
- Improve README parsing
- Add UI layer
- Add test coverage

Feel free to open a Pull Request.

---

# 📜 License

This project is open for educational and personal use.

---

# ⭐ Final Note

Consistency is more important than intensity.

Automate the boring.
Focus on solving.
Ship daily.
Stay consistent.

Happy Coding 🚀