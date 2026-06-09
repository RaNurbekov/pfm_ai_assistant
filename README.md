# 💰 PFM AI Assistant — Personal Finance Manager

> **End-to-end AI-powered Personal Finance Manager for bank transaction analysis**
> NLP categorization → Interactive Dashboard → Anomaly Detection → Forecast → Voice Assistant → Telegram Bot

---

## 🚀 Live Demo

🔗 **[pfm-ai-assistant.streamlit.app](https://pfm-ai-assistant.streamlit.app)**

---

## 🎯 Business Problem

Banks face a universal challenge:
> *"Users have no idea where their money goes — leading to poor financial decisions, overdrafts, and customer churn."*

This project solves it by automatically transforming raw, messy bank transaction data into actionable financial insights — localized for the **Kazakhstani market 🇰🇿** with behavioral simulation and AI-powered analysis.

---

## 📊 Complete Feature List

```
Raw Bank Transactions (116,201 rows)
        │
        ▼
🧹 Data Cleaning Pipeline
   • Remove duplicates & nulls
   • Normalize transaction descriptions
   • Create AMOUNT + TYPE columns
        │
        ▼
🏷️ Smart Categorization Engine (83.5% coverage)
   • 13 spending categories
   • Rule-based NLP on transaction descriptions
   • KZ merchant support (Glovo, Kaspi, inDrive, Air Astana)
        │
        ▼
📊 Interactive Streamlit Dashboard
   • KPI Cards — Income, Spending, Net Balance
   • Spending breakdown by category (pie chart)
   • Monthly spending trend (line chart)
   • Income vs Expenses comparison (bar chart)
   • Top 10 categories ranking
   • Recent transactions table
   • Filters: Account, Date Range, Transaction Type
        │
        ├──► 🎯 Budget Tracker
        │    • Set monthly limits per category
        │    • Real-time progress bars
        │    • Over-budget alerts
        │
        ├──► 🚨 Anomaly Detection
        │    • Z-Score per category
        │    • Velocity Check (too many transactions/day)
        │    • Risk scoring: Low / Medium / High
        │    • Scatter chart — anomalies highlighted
        │
        ├──► 🔮 Spending Forecast (Prophet ML)
        │    • 3-month prediction
        │    • 80% confidence intervals
        │    • Seasonal patterns detection
        │    • Trend alerts (increasing / stable / decreasing)
        │
        ├──► 🎙️ Voice Financial Assistant
        │    • Whisper Large v3 — Speech-to-Text (Groq)
        │    • Llama 3.3-70B — Answer generation
        │    • gTTS — Text-to-Speech response
        │    • Supports Russian & English
        │
        ├──► 🤖 AI Financial Advisor (Llama 3.3-70B)
        │    • Spending pattern analysis
        │    • Warning signs detection
        │    • Top 3 personalized recommendations
        │    • Savings rate gauge visualization
        │
        ├──► 📄 PDF Report Generator
        │    • Professional PDF with charts
        │    • Category breakdown table
        │    • Budget + anomaly summary
        │    • AI insights section
        │
        ├──► 💱 Multi-currency Support
        │    • 8 currencies (KZT, USD, EUR, RUB, GBP, CNY, INR, TRY)
        │    • Live exchange rates with daily caching
        │    • Quick currency converter widget
        │
        └──► 📱 Telegram Weekly Bot
             • Automated weekly spending reports
             • Top categories & merchants
             • AI-generated insight per report
             • Scheduled every Monday 9:00 AM
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Data Processing** | Python, Pandas, NumPy |
| **Categorization** | Rule-based NLP Engine (custom) |
| **Visualization** | Plotly Express, Plotly Graph Objects |
| **Frontend** | Streamlit |
| **ML Forecast** | Prophet (Facebook) |
| **Anomaly Detection** | SciPy (Z-Score), Custom Velocity Check |
| **LLM Engine** | Llama 3.3-70B via Groq API |
| **Voice STT** | Whisper Large v3 via Groq API |
| **Voice TTS** | gTTS (Google Text-to-Speech) |
| **PDF Generation** | ReportLab |
| **Telegram Bot** | python-telegram-bot |
| **Currency API** | ExchangeRate API (free tier) |
| **KZ Simulation** | Custom behavioral simulator (3 profiles) |
| **Containerization** | Docker |

---

## 🇰🇿 Kazakhstan Localization

Specifically designed for the Kazakhstani fintech market:

**KZ Merchant Support:**
```
Glovo, Wolt          → Food & Dining
Kaspi Shop           → Shopping
inDrive, Yandex Go   → Transport
Air Astana           → Transport
Kcell, Beeline KZ    → Utilities
Kinopark, Chaplin    → Entertainment
Kaspi Kredit         → Loan & Finance
```

**Behavioral Simulation — 3 KZ Customer Profiles:**

| Profile | Monthly Income | Spending Focus |
|---|---|---|
| Student (18-23) | ₸80,000 | Food, Transport, Entertainment |
| Young Professional (25-30) | ₸350,000 | Shopping, Food, Loan payments |
| Family (35-45) | ₸600,000 | Groceries, Utilities, Education |

Each profile generates **12 months** of realistic transactions with seasonal patterns — December spending spike +40%, January savings mode.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/RaNurbekov/pfm_ai_assistant.git
cd pfm_ai_assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get free API keys
- **Groq API** (LLM + Whisper): [console.groq.com](https://console.groq.com) — free
- **Telegram Bot**: [@BotFather](https://t.me/BotFather) on Telegram — free

### 4. Create `.env` file
```env
GROQ_API_KEY=your_groq_key
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 5. Generate KZ simulated data
```bash
python kz_simulator.py
# → generates kz_transactions.csv (2,709 transactions, 3 accounts)
```

### 6. Launch dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) 🎉

### 7. Send Telegram report
```bash
python telegram_bot.py test    # test connection
python telegram_bot.py now     # send report now
python telegram_bot.py schedule  # start weekly scheduler
```

---

## 🐳 Docker

```bash
docker build -t pfm-ai-assistant .
docker run -p 8501:8501 --env-file .env pfm-ai-assistant
```

---

## 📁 Project Structure

```
pfm_ai_assistant/
├── app.py                  # Main Streamlit dashboard (all features)
├── kz_simulator.py         # KZ behavioral transaction simulator
├── kz_categorizer.py       # KZ merchant categorization rules
├── anomaly_detector.py     # Z-Score + Velocity anomaly detection
├── forecaster.py           # Prophet ML spending forecast
├── budget_tracker.py       # Budget limits + progress tracking
├── voice_insights.py       # Whisper STT + Llama + gTTS pipeline
├── pdf_report.py           # ReportLab PDF generator
├── telegram_bot.py         # Weekly Telegram report bot
├── kz_transactions.csv     # Simulated KZ data (generated)
├── budgets.json            # User budget settings (generated)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 📈 Data Pipeline Results

| Stage | Rows | Coverage |
|---|---|---|
| Raw data | 116,201 | — |
| After cleaning | 113,702 | — |
| Rule-based categorization | 94,893 | **83.5%** |
| Uncategorized (Other) | 18,809 | 16.5% |

**13 Categories:**
`Income` `Transfer` `ATM & Cash` `Utilities` `Entertainment`
`Shopping` `Transport` `Loan & Finance` `Tax & Charges`
`Payment Gateway` `Food & Dining` `Healthcare` `Government`

---

## 🔮 Roadmap (v2.0)

| Feature | Description |
|---|---|
| **DistilBERT categorizer** | Replace rules with fine-tuned NLP model (95%+ coverage) |
| **Real KZ bank data** | Integration with Kaspi API when available |
| **WhatsApp Bot** | Extend notifications to WhatsApp Business API |
| **Investment Tracker** | Track stocks and crypto alongside bank spending |
| **CI/CD Pipeline** | GitHub Actions for automated testing and deployment |

---

## 🔗 Related Projects

Part of a Fintech ML ecosystem:

- [**fraud-detection-api**](https://github.com/RaNurbekov/fraud-detection-api) — Real-time fraud detection with Redis + A/B Testing
- [**credit-risk-api**](https://github.com/RaNurbekov/credit-scoring-ml-api.) — Credit scoring with MLflow + SHAP + Evidently AI
- [**fraud-gnn**](https://github.com/RaNurbekov/fraud-gnn) — Graph Neural Networks for fraud detection
- [**bank-ai-assistant**](https://github.com/RaNurbekov/llm_bot-ai_bank_assistant-) — RAG chatbot with Qdrant + Llama 3

> 💡 **Product vision:** transactions get categorized (this project) → fraud gets detected →
> credit risk assessed → customer gets AI advice. That's the full fintech ML stack.

---

## 📫 Author

**Rashid Nurbekov** — ML Engineer | Fintech & Generative AI | Almaty, Kazakhstan 🇰🇿

[![Telegram](https://img.shields.io/badge/Telegram-@RaNurbek-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/RaNurbek)
[![Email](https://img.shields.io/badge/Email-nurbekovrashidjob@gmail.com-D14836?style=flat&logo=gmail&logoColor=white)](mailto:nurbekovrashidjob@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-RaNurbekov-181717?style=flat&logo=github&logoColor=white)](https://github.com/RaNurbekov)


