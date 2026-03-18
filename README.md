# Jenkins Secret Manager

Student Name: Ayush Madhukar
Registration No: 23FE10CSE00334
Course: CSE3253 DevOps [PE6]
Semester: VI (2025–2026)
Project Type: Jenkins & CI
Difficulty: Intermediate

---

## Project Overview

### Problem Statement
Jenkins pipelines need access to sensitive credentials — API keys, database passwords, tokens — but storing these in plain text or hardcoding them in Jenkinsfiles is a serious security risk. This project provides a secure, web-based management layer for Jenkins credentials, with encryption, expiry tracking, rotation, and a full audit trail.

### Objectives
- [x] Build a web dashboard to add, view, rotate, and delete Jenkins secrets
- [x] Encrypt all secrets at rest using Fernet symmetric encryption
- [x] Sync secrets automatically to Jenkins via the Credentials REST API
- [x] Track secret expiry and alert for secrets expiring within 7 days
- [x] Maintain a tamper-evident audit log of all actions
- [x] Containerize the application with Docker and Jenkins side-by-side

### Key Features
- AES-128 encryption via Python `cryptography` (Fernet)
- One-click secret rotation synced to Jenkins
- Expiry tracking with dashboard alerts
- Full audit log (who did what and when)
- REST API (`/api/secrets`, `/api/health`) for pipeline integration
- Docker Compose setup with Jenkins LTS included

---

## Technology Stack

### Core Technologies
- **Programming Language:** Python 3.11
- **Framework:** Flask 3.0
- **Database:** SQLite (dev) / PostgreSQL (prod)

### DevOps Tools
- **Version Control:** Git
- **CI/CD:** Jenkins (Jenkinsfile in `pipelines/`)
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Kubernetes (manifests in `infrastructure/kubernetes/`)
- **Monitoring:** Nagios (configs in `monitoring/nagios/`)

---

## Getting Started

### Prerequisites
- [ ] Docker Desktop v20.10+
- [ ] Git 2.30+
- [ ] Python 3.11+ (for local dev without Docker)

### Installation (Docker — recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/Ayushmadhukar18/devopsprojectjenkinssecretmanager.git
   cd devopsprojectjenkinssecretmanager
   ```

2. Copy the env template:
   ```bash
   cp src/config/.env.example .env
   # Edit .env — at minimum generate an ENCRYPTION_KEY
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. Start the stack:
   ```bash
   docker-compose -f infrastructure/docker/docker-compose.yml up --build
   ```

4. Access:
   - **Secret Manager:** http://localhost:5000
   - **Jenkins:** http://localhost:8080

### Installation (Without Docker)

```bash
cd src/main
pip install -r requirements.txt
cp ../config/.env.example .env   # fill in values
cd app
python app.py
```

---

## Project Structure

```
devopsprojectjenkinssecretmanager/
├── src/
│   ├── main/
│   │   ├── app/            Flask application (app.py, models, templates)
│   │   └── requirements.txt
│   ├── config/             Environment config templates
│   └── test/
├── infrastructure/
│   ├── docker/             Dockerfile + docker-compose.yml
│   └── kubernetes/         K8s manifests
├── pipelines/
│   └── Jenkinsfile         CI/CD pipeline
├── tests/
│   ├── unit/               Pytest unit tests
│   └── selenium/           Browser automation tests
└── monitoring/
    └── nagios/             Nagios configs
```

---

## CI/CD Pipeline

The `pipelines/Jenkinsfile` defines these stages:

1. **Checkout** — pull source from GitHub
2. **Code Quality** — flake8 linting
3. **Build** — build Docker image
4. **Test** — run pytest unit tests
5. **Security Scan** — Trivy image vulnerability scan
6. **Deploy Staging** — auto on `develop` branch
7. **Deploy Production** — manual approval on `main`

---

## Testing

```bash
# Unit tests
cd src && python -m pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=main/app --cov-report=term
```

---

## Security Measures
- [x] Fernet symmetric encryption for all stored secret values
- [x] `.env` based configuration — no secrets in code
- [x] Non-root Docker user
- [x] Input sanitization on secret names
- [x] Trivy vulnerability scanning in CI pipeline

---

## Acknowledgments
- Course Instructor: Mr. Jay Shankar Sharma
- Jenkins Credentials API documentation
- Python `cryptography` library

## Contact
Student: Ayush Madhukar
GitHub: https://github.com/Ayushmadhukar18
Course Coordinator: Mr. Jay Shankar Sharma — Thursday & Friday, 5–6 PM, LHC 308F