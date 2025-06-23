# 🧾 AI-Based Invoice Management System

An AI-powered, full-stack **Invoice Management System** designed to automate the extraction, processing, and storage of invoice data using cutting-edge OCR and computer vision techniques. The application runs inside Docker containers using `docker-compose` for seamless multi-service orchestration.

---

## 🚀 Overview

Manual invoice handling can be error-prone, inefficient, and difficult to scale. This project aims to solve those issues by using AI for automatic data extraction from invoices and storing the information in a structured SQL database — all within a fully containerized architecture.

---

## 🛠️ Tech Stack

### 💻 Frontend
- **HTML5**
- **CSS3**
- **JavaScript**

### 🧠 Backend
- **Python**

### 🗃️ Database
- **SQL** (MySQL/PostgreSQL based on your setup)

### 🐳 Containerization
- **Docker**
- **Docker Compose**

---

## ⚙️ Core Frameworks & Libraries

- **OpenCV** – Image preprocessing and region detection  
- **NumPy** – Matrix operations and data manipulation  
- **Pytesseract** – OCR engine to extract text from images  
- **pdfplumber** – PDF content extraction and table parsing  
- **Pandas** – Data formatting and cleaning  
- **Flask / FastAPI** – REST API server (choose based on your actual setup)  
- **Tesseract-OCR** – External dependency for text recognition

---

## 📦 Features

- 📄 Upload invoices in PDF or image format  
- 🧠 Extract invoice data (Invoice Number, Date, Vendor, Total, etc.) using OCR  
- 💾 Store extracted data in an SQL database  
- 🌐 View and manage invoices via a web dashboard  
- 🔎 Search and filter invoice records  
- 🐳 Fully containerized setup using Docker  
- 🔗 `docker-compose.yml` to run multiple services (frontend, backend, database) in parallel
