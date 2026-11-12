# AI Career Copilot

An AI-powered resume analyzer built with Python and Flask to help job seekers evaluate their resumes and improve their job applications.

## Features

- User registration and login
- Resume upload (PDF and DOCX)
- AI-powered resume analysis
- Resume analysis reports
- Analysis history
- Database integration

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **Database:** TiDB / MySQL
- **AI Integration:** OpenAI API
- **Libraries:** PyPDF2, python-docx, SQLAlchemy

## Project Structure

```text
ai_career_copilot/
│
├── app.py
├── ai.py
├── db.py
├── models.py
├── templates/
├── .gitignore
├── .env.example
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Dhatrakrohini/ai-career-copilot.git
```

2. Open the project folder:

```bash
cd ai-career-copilot
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate it on Windows:

```powershell
venv\Scripts\activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Configure your environment variables in a local `.env` file.

7. Run the application:

```bash
python app.py
```

## Security

API keys, database credentials, and secret keys are stored in environment variables and should never be committed to GitHub.

## Author

**Rohini Dhatrak**

GitHub: https://github.com/Dhatrakrohini

LinkedIn: https://www.linkedin.com/in/rohinidhatrak/