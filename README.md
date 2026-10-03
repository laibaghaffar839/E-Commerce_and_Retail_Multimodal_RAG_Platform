# Multimodal AI-Powered Retail Workspace RAG Platform

## Industry

**E-commerce & Retail Intelligence**

---

## Problem Statement

Retail and e-commerce teams manage large amounts of business information scattered across different file formats, including supplier contracts, product catalogs, inventory spreadsheets, presentations, images, audio recordings, and promotional videos. Finding specific information manually across these files can be time-consuming and may lead to operational delays and loss of important context.

This platform unifies retail business information into a secure, room-based Retrieval-Augmented Generation (RAG) system. Users can create dedicated workspace rooms, upload multiple types of files, and ask questions in natural language. The system retrieves relevant information from uploaded files and generates grounded answers with source citations.

---

## Installation Guide

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

For macOS or Linux:

```bash
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```
### Recommended practice

Always update `requirements.txt` after installing new packages:

```bash
pip install new-package
pip freeze > requirements.txt
```

---

## PostgreSQL Database Setup

The application uses PostgreSQL with SQLAlchemy ORM for persistent data storage.

Make sure PostgreSQL is installed and running on your system.

Create a PostgreSQL database for the project and configure the database connection in the `.env` file.

Example:

```env
DATABASE_URL="postgresql://username:password@localhost:5433/database_name"  # you can use your port like 5432
```

Replace the following values according to your PostgreSQL configuration:

* `username` — PostgreSQL username
* `password` — PostgreSQL password
* `5433` — PostgreSQL port
* `database_name` — Project database name

The database stores:

* User accounts
* Chat rooms
* Chat messages
* Uploaded file metadata

---

## Environment Variables

Create a `.env` file in the root directory of the project.

```env
# Application Settings
SECRET_KEY="your-super-secret-jwt-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Groq API Key
GROQ_API_KEY="gsk_your_groq_api_key_here"

# PostgreSQL Database
DATABASE_URL="postgresql://username:password@localhost:5433/database_name"
```

Never commit your `.env` file or API keys to GitHub. Make sure `.env` is included in `.gitignore`.

---

## Running the Application

The application requires two running processes:

1. FastAPI backend
2. Streamlit frontend

### Step 1: Start FastAPI Backend

```bash
uvicorn main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

Docs:

```text
http://127.0.0.1:8000/docs
```

### Step 2: Start Streamlit Frontend

```bash
streamlit run streamlit_app.py
```

Frontend:

```text
http://localhost:8501
```

---

## Project Summary

This project demonstrates a full-stack **Multimodal RAG system** combining FastAPI, Streamlit, PostgreSQL, Qdrant, and Groq LLMs to enable intelligent document understanding for retail and e-commerce workflows.

