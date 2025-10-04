# 🧪 Test Case Generator

An AI-powered web application that automatically generates comprehensive test cases from user stories using Google's Gemini AI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)

## ✨ Features

- 🤖 **AI-Powered Generation**: Uses Google Gemini 2.5 Pro to generate intelligent test cases
- 📝 **Dual Input Methods**: Enter user stories directly or upload text files
- 📊 **Live Logs Panel**: Real-time monitoring of the generation process
- 📁 **Automatic File Management**: Timestamped CSV files with proper organization
- 🎨 **Modern UI**: Beautiful, responsive interface with smooth animations
- ⬇️ **Direct Download**: One-click download of generated CSV files
- 🔍 **Structured Output**: Test cases include ID, Title, Steps, Expected Results, and Acceptance Criteria
- 💾 **Export Logs**: Download logs for debugging and auditing

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Account with Gemini API access
- Google API credentials configured

## 🚀 Installation
### Setup Instructions
```dtd
pip install Flask==3.0.0
pip install langchain-google-genai
pip install pandas
pip install openpyxl
```
OR
```dtd
pip install -r requirements.txt
```
### 1. Clone the repository
```bash
git clone <your-repo-url>
cd test-case-generator
```

### 2. Project Tree Structure
```
test-case-generator/
├── app.py                          # Flask application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── services/
│   ├── __init__.py                # Package initializer
│   ├── gemini_service.py          # Gemini AI integration
│   └── csv_service.py             # CSV file operations
├── templates/
│   └── index.html                 # Main web interface
├── static/
│   ├── css/
│   │   └── style.css              # Application styles
│   └── js/
│       └── main.js                # Frontend logic
└── generated_test_cases/          # Output directory (auto-created)
```