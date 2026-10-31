# Instahyre Auto-Application Bot 🚀

A Python-based browser automation bot that automates job applications on [Instahyre](https://www.instahyre.com/).

The bot uses **Playwright** to log in to your Instahyre account, apply experience filters, open job listings, and continuously submit applications with minimal manual intervention.

## ✨ Features

- **Automated Login:** Logs in using credentials stored securely in a separate `.env` file.
- **Persistent Browser Session:** Saves browser session data to avoid logging in every time.
- **Experience Filter:** Automatically applies the 4-year experience filter using Instahyre's URL parameters.
- **Automatic Job Opening:** Opens the first available job using the View Job button.
- **Continuous Auto-Application:** Automatically clicks Apply on subsequent job listings.
- **Confirmation Handling:** Detects optional confirmation popups such as Apply to 1 job, Apply to 2 jobs, etc.
- **Automatic Job Detection:** Detects when the next job application becomes available.
- **Graceful Stopping:** Press `CTRL + C` to stop the automation.
- **Lightweight Logging:** Displays basic application progress in the terminal.

## 🛠️ Tech Stack

- Python
- Playwright
- Chromium
- Python Dotenv

## 📁 Project Structure

```text
InstaHyre automated bot/
│
├── instahyre_login.py
│
├── .env
│
├── instahyre_browser_profile/
│
├── README.md
│
└── requirements.txt
```

| File / Folder | Description |
|---|---|
| `instahyre_login.py` | Main automation script |
| `.env` | Stores Instahyre login credentials |
| `instahyre_browser_profile/` | Stores persistent browser session |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
```

Navigate to the project directory:

```bash
cd "InstaHyre automated bot"
```

### 2. Create a virtual environment (Optional)

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install playwright python-dotenv
```

### 4. Install Chromium

```bash
python -m playwright install chromium
```

## 🔐 Environment Configuration

Create a `.env` file in the root directory.

Add your Instahyre credentials:

```env
INSTAHYRE_EMAIL=your_email@gmail.com
INSTAHYRE_PASSWORD=your_password
```

**Important:** Never commit your `.env` file or browser profile to GitHub.

Add the following to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
instahyre_browser_profile/
```

## ▶️ Running the Bot

Execute the following command:

```bash
python instahyre_login.py
```

The bot will:

1. Launch Chromium.
2. Check your existing Instahyre login session.
3. Log in if authentication is required.
4. Navigate to the filtered opportunities page.
5. Apply the 4-year experience filter.
6. Open the first job listing.
7. Start automatically applying to jobs.

## 🔄 Automation Workflow

```text
        START
          |
          v
    Launch Browser
          |
          v
   Check Login Session
          |
          v
    Login if Required
          |
          v
 Apply 4-Year Experience
          |
          v
   Open First View Job
          |
          v
      Click Apply
          |
          v
  Confirmation Popup?
       /       \
     Yes        No
      |          |
      v          |
 Apply to N Jobs |
      |          |
      +----+-----+
           |
           v
    Detect Next Job
           |
           v
      Click Apply
           |
           v
       Repeat
```

## 🎯 Important URLs

**Instahyre Login:**

https://www.instahyre.com/login/

**Opportunities without experience filter:**

https://www.instahyre.com/candidate/opportunities/?matching=true

**Opportunities with 4-year experience filter:**

https://www.instahyre.com/candidate/opportunities/?experience=4&matching=true

## 🛑 Stopping the Bot

To stop the automation at any time:

```text
CTRL + C
```

The bot will stop processing further applications and close the browser.

## ⚠️ Notes

- Keep the browser profile directory intact to retain your login session.
- If Instahyre requires OTP or CAPTCHA verification, complete it manually.
- Do not delete the browser profile unless you want to establish a fresh session.
- The bot relies on Instahyre's current page structure and may require updates if the website changes.
- Review job descriptions and eligibility before applying. Automated applications should comply with Instahyre's terms and applicable usage restrictions.
- Avoid running multiple instances simultaneously.

## 🔮 Future Enhancements

Potential improvements for future versions:

- Job title and keyword filtering.
- Location-based filtering.
- Salary-based filtering.
- Company exclusion list.
- Job description matching against resume.
- AI-powered job relevance scoring.
- Application history tracking.
- Excel export of applied jobs.
- Configurable maximum application limit.
- Automatic scheduling.

---

**Built with Python and Playwright.**

*Instahyre Auto-Application Bot — Automating the repetitive parts of job searching.*