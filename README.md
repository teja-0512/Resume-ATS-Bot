# 🤖 Resume ATS Telegram Bot

An AI-powered Telegram bot that analyzes resumes against a Job Description (JD) using ATS (Applicant Tracking System) principles. The bot compares multiple resumes, evaluates their suitability for a given role, and provides detailed feedback directly in Telegram.

## ✨ Features

- 💼 Enter a Job Role
- 📄 Upload or paste a Job Description
- 📑 Upload two resumes (PDF/DOCX)
- 🎯 ATS Match Score for each resume
- ✅ Matched Skills Detection
- ❌ Missing Skills Identification
- 💼 Experience Match Analysis
- 🎓 Education Match Analysis
- 💪 Resume Strengths
- ⚠️ Resume Weaknesses
- 💡 Personalized Improvement Suggestions
- ⭐ Hiring Recommendation
- 🏆 Best Resume Selection
- 🤖 AI-powered analysis using OpenAI
- 📱 Instant results directly in Telegram

---

## 🛠️ Tech Stack

- Python
- python-telegram-bot
- OpenAI API
- PyPDF2
- python-docx
- Regular Expressions (Regex)
- Git & GitHub

---

## 📂 Project Structure

```
ResumeCompareBot/
│
├── bot.py              # Telegram bot workflow
├── compare.py          # ATS scoring engine
├── parser.py           # Resume & JD parser
├── ai.py               # OpenAI integration
├── config.py           # Configuration
├── requirements.txt
├── .gitignore
├── uploads/
└── README.md
```

---

## 🚀 Workflow

1. Start the bot using `/compare`
2. Enter the Job Role
3. Paste or upload the Job Description
4. Upload Resume 1
5. Upload Resume 2
6. The bot analyzes both resumes against the JD
7. Receive a detailed ATS report in Telegram

---

## 📊 Sample Output

```
ATS Resume Analysis

Job Role:
Python Full Stack Developer

Resume 1
✔ ATS Score: 88%
✔ Matched Skills
✔ Experience Match
✔ Education Match
✔ Strengths
✔ Weaknesses
✔ Suggestions

Resume 2
✔ ATS Score: 81%
✔ Matched Skills
✔ Experience Match
✔ Education Match
✔ Strengths
✔ Weaknesses
✔ Suggestions

🏆 Best Candidate: Resume 1
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/teja-0512/Resume_ATS-TelegramBot.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

Run the bot:

```bash
python bot.py
```

---

## 📌 Future Enhancements

- Resume ranking for multiple candidates
- ATS score visualization
- Recruiter dashboard
- Database integration
- Cloud deployment
- Support for multiple job descriptions
- Advanced AI feedback

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Teja**

Computer Science Engineering Student | Python Developer | AI & Full Stack Enthusiast
