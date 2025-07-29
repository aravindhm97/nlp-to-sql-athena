# NLP-Powered SQL Query Tool with AWS Athena

![Auto-Deployment Status](https://github.com/yourusername/nlp-to-sql-athena/actions/workflows/deploy.yml/badge.svg)
![Streamlit App](https://img.shields.io/badge/Streamlit-Deployed-green)

A **fully automated, 100% free-tier AWS project** that converts English queries to SQL using a real NLP model, executes on Amazon Athena, and visualizes results via Streamlit. Features **one-click deployment** via GitHub Actions.

## ✨ Why This Stands Out
- **Real NLP Model**: Uses `tscholak/cxmefzzi` (Hugging Face free tier)
- **Zero Manual Setup**: GitHub Actions handles all AWS provisioning
- **True Auto-Deployment**: Push to main → live Streamlit app in 5 minutes
- **Production-Grade CI/CD**: Enterprise-level deployment pipeline
- **100% Free Tier Compliant**: All components within AWS free limits

## 🚀 One-Click Deployment (30 Seconds)

### 1. Fork this repository
[![Fork on GitHub](https://img.shields.io/badge/Fork_Repository-GitHub-green?logo=github)](https://github.com/yourusername/nlp-to-sql-athena/fork)

### 2. Configure Secrets
Go to **Settings → Secrets → New repository secret** and add:
```env
AWS_ACCESS_KEY_ID = YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = YOUR_AWS_SECRET_KEY
HF_TOKEN = YOUR_HF_TOKEN (get at hf.co/settings/tokens)
STREAMLIT_SHARING_TOKEN = YOUR_STREAMLIT_TOKEN (get at share.streamlit.io)
