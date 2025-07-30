# 🧠 Enhanced Git

**Enhanced Git** is an API built with **FastAPI** using **Python 3.12**. It aims to provide a richer experience around GitHub and GitLab project data. The project is containerized with Docker and includes tools for development, testing, linting, and code coverage.

---

## 🚀 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- Python 3.12
- Docker & Docker Compose
- Pytest — for unit testing
- Pylint — for code linting
- Coverage — for test coverage reports

---

## 📦 Installation

### .env

Create a venv with these variables : 

```
BDD_USER=""
BDD_PSWD=""
BDD_HOST=""
BDD_PORT=
BDD_NAME=""

BEARER_SECRET_TOKEN=""
REFRESH_SECRET_TOKEN=""

GITHUB_CLIENT=""
GITHUB_CLIENT_SECRET=""

FRONT_URL=""
```

### 🔁 Option 1: Run with Docker

1. Make sure **Docker** and **Docker Compose** are installed.
2. Start the services:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at: http://localhost:8000

### 🔁 Option 2: Local Setup (with venv)

1. Create and activate a virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update database:
   ```bash
   alembic upgrade head
   ```
3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

### ✅ Running Tests

To execute unit tests and generate a coverage report: 
 
   ```bash 
    pytest \
    --cov=routers \
    --cov=services \
    --cov=repositories \
    --cov=utils \
    --cov=models \
    --cov=schemas \
    --cov=main \
    --cov-report=term-missing
   ``` 

This will display line-by-line coverage information and highlight untested lines.

### 🔍 Linting

To check code quality using `pylint`:

```
pylint . 
```
You can configure rules using a .pylintrc file.


