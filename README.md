# 💰 SEC 13F Holdings Chat

A free public web app to explore institutional investor holdings using natural language, powered by Snowflake Cortex.

![SEC 13F Chat](https://img.shields.io/badge/Powered%20by-Snowflake%20Cortex-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Features

- 💬 Natural language queries about hedge fund holdings
- 📊 Real-time data from SEC 13F filings
- 🤖 Powered by Snowflake Cortex Agent (Text-to-SQL)
- 📱 Mobile-friendly interface
- 🔒 Secure key pair authentication (no passwords)
- 🆓 Free to use

## 📋 Prerequisites

- Snowflake account with Cortex enabled
- SEC 13F data loaded into Snowflake
- Cortex Agent configured with a Semantic View
- Python 3.8+

## 🛠️ Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/sameer629-code/sec13f-chat-app.git
cd sec13f-chat-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your Snowflake credentials

# 4. Run the app
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud (Free)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/sec13f-chat-app.git
git push -u origin main
```

### Step 2: Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Add secrets in "Advanced settings" (copy contents from `secrets.toml.example` and fill in your values)
6. Click "Deploy!"

## 🔒 Authentication

This app uses **Key Pair authentication** (no passwords stored):

1. Generate an RSA key pair:
```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

2. Assign the public key to your Snowflake user:
```sql
ALTER USER your_username SET RSA_PUBLIC_KEY='<paste public key content>';
```

3. Add the private key to `.streamlit/secrets.toml`

## 💡 Example Questions

- "What are the top 10 most widely held stocks?"
- "What is the total AUM for the top 10 institutional managers?"
- "Which funds are increasing their Snowflake holdings?"
- "In the last four quarters, which stocks had the most consecutive position increases?"
- "Which stocks had a 10x increase in institutional holders?"

## 📊 Data Coverage

| Quarter | Holdings As Of | Filed By |
|---------|----------------|----------|
| Q4 2024 | Dec 31, 2024 | Feb 14, 2025 |
| Q1 2025 | Mar 31, 2025 | May 15, 2025 |
| Q2 2025 | Jun 30, 2025 | Aug 14, 2025 |
| Q3 2025 | Sep 30, 2025 | Nov 14, 2025 |

## 🔧 Technology Stack

- **Snowflake Cortex Agent** — AI orchestration & Text-to-SQL
- **Semantic Views & Dynamic Tables** — Data abstraction layer
- **REST API with JWT** — Secure agent invocation
- **Streamlit** — Frontend framework

## 📄 License

MIT License - Free to use and modify.

## 🙏 Credits

- Data: [SEC EDGAR](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets)
- AI: [Snowflake Cortex](https://www.snowflake.com/en/data-cloud/cortex/)
- UI: [Streamlit](https://streamlit.io/)
