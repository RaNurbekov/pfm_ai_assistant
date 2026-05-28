# 💰 PFM AI Assistant — Personal Finance Manager

> **End-to-end AI-powered Personal Finance Manager for bank transaction analysis**
> Rule-based categorization → Interactive Dashboard → LLM Financial Advisor (Llama 3)

---

## 🎯 Business Problem

Banks like  Revolut, and N26 all face the same challenge:
> *"Users have no idea where their money goes — leading to poor financial decisions, overdrafts, and customer churn."*

This project solves it by automatically transforming raw, messy bank transaction data into actionable financial insights — the same way production PFM systems work at top fintech companies.

---

## 🚀 Live Demo

> Run locally — see instructions below

---

## 📊 What It Does

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
🏷️ AI Categorization Engine (83.5% coverage)
   • 13 spending categories
   • Rule-based NLP on transaction descriptions
   • Handles Indian bank transaction formats
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
        ▼
🤖 AI Financial Advisor (Llama 3.3-70B via Groq)
   • Spending pattern analysis
   • Warning signs detection
   • Top 3 personalized recommendations
   • Monthly savings goal calculation
   • Savings rate gauge visualization
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Data Processing** | Python, Pandas, NumPy |
| **Categorization** | Rule-based NLP Engine (custom) |
| **Visualization** | Plotly Express, Plotly Graph Objects |
| **Frontend** | Streamlit |
| **LLM Engine** | Llama 3.3-70B via Groq API |
| **Environment** | python-dotenv |
| **Dataset** | Bank Transaction Data (Kaggle, 116K rows) |

---

## 🔑 Key Features

### 1. Smart Categorization Engine
Custom rule-based NLP categorizer that handles real bank transaction noise:
```
"FDRL/NATIONAL ELECTRONIC F"  → Transfer
"BSES RAJDHANI POWER LIMIT"   → Utilities
"PVR LIMITED"                  → Entertainment
"INDIAFORENSIC AEPS NPCI WDL" → ATM & Cash
```
**13 categories | 83.5% coverage | 113,702 transactions**

### 2. Interactive Dashboard
4 dynamic charts with real-time filters by account, date range, and transaction type. Built with Plotly for smooth interactivity.

### 3. AI Financial Advisor
Llama 3.3-70B analyzes real spending data and generates:
- Personalized spending analysis with exact numbers
- Warning signs (overspending, unusual patterns)
- Top 3 actionable recommendations
- Realistic savings goal based on actual income

**Smart filtering:** Transfers and ATM withdrawals excluded from spending analysis — only real expenses analyzed (same approach used by Mint and KOHO).

### 4. Savings Rate Gauge
Visual gauge showing savings rate vs 20% recommended benchmark — color coded:
- 🔴 Red: 0-10% (critical)
- 🟡 Yellow: 10-20% (needs improvement)
- 🟢 Green: 20%+ (healthy)

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/RaNurbekov/pfm-ai-assistant.git
cd pfm-ai-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get free Groq API key
Sign up at [console.groq.com](https://console.groq.com) — it's free.

### 4. Create `.env` file
```env
GROQ_API_KEY=your_key_here
```

### 5. Download dataset
Download [Bank Transaction Data](https://www.kaggle.com/datasets/apoorvwatsky/bank-transaction-data) from Kaggle.
Place `bank_transactions.csv` in the project root.

### 6. Run data pipeline
```bash
python data_pipeline.py
# → generates bank_transactions_clean.csv
```

### 7. Launch dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) 🎉

---

## 📁 Project Structure

```
pfm-ai-assistant/
├── app.py                      # Streamlit dashboard + AI Advisor
├── data_pipeline.py            # Cleaning + categorization pipeline
├── bank_transactions_clean.csv # Processed dataset (generated)
├── requirements.txt
├── .env                        # API keys (not committed)
├── .gitignore
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

## 💡 How It Compares to Production PFM Systems

| Feature | This Project | Mint | Kaspi PFM |
|---|---|---|---|
| Auto-categorization | ✅ Rule-based | ✅ ML-based | ✅ ML-based |
| Spending dashboard | ✅ | ✅ | ✅ |
| AI recommendations | ✅ Llama 3 | ❌ | ❌ |
| Open source | ✅ | ❌ | ❌ |
| Custom LLM advisor | ✅ | ❌ | ❌ |

---

## 🔮 Roadmap (v2.0)

| Feature | Description |
|---|---|
| **DistilBERT categorizer** | Replace rules with fine-tuned NLP model |
| **Anomaly Detection** | Flag unusual transactions automatically |
| **Budget Tracker** | Set limits per category, track progress |
| **Multi-language** | Support Russian + Kazakh transaction formats |
| **Docker deployment** | Containerize for production deployment |

---

## 🔗 Related Projects

This project is part of a Fintech ML ecosystem:

- [**fraud-detection-api**](https://github.com/RaNurbekov/fraud-detection-api) — Real-time fraud detection with Redis + A/B Testing
- [**credit-risk-api**](https://github.com/RaNurbekov/credit-scoring-ml-api.) — Credit scoring with MLflow + SHAP + Evidently AI
- [**bank-ai-assistant**](https://github.com/RaNurbekov/llm_bot-ai_bank_assistant-) — RAG chatbot with Qdrant + Llama 3
- [**bank-transaction-categorizer**](https://github.com/RaNurbekov/Transaction-Categorizer-Deep-Learning-PyTorch-Hugging-Face-NLP-) — DistilBERT fine-tuning for transaction categorization

> 💡 **Product vision:** Combine all four projects into a complete bank AI platform —
> transactions get categorized → fraud gets detected → credit risk assessed → customer gets AI advice.
> That's the full fintech ML stack.

---

## 📫 Author

**Rashid Nurbekov** — ML Engineer | Fintech & Generative AI

[![Telegram](https://img.shields.io/badge/Telegram-@Ytyglika-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/Ytyglika)
[![Email](https://img.shields.io/badge/Email-nurbekovrashidjob@gmail.com-D14836?style=flat&logo=gmail&logoColor=white)](mailto:nurbekovrashidjob@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-RaNurbekov-181717?style=flat&logo=github&logoColor=white)](https://github.com/RaNurbekov)