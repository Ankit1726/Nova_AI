<div align="center">

# 🚀 Nova Agent

### AI Personal Assistant built with LangGraph, RAG & Human Approval

An intelligent AI assistant that combines **LLMs, RAG, Tool Calling, Persistent Memory, and Human-in-the-Loop approval** inside a modern Streamlit interface.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-purple?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLM-orange?style=flat-square)

</div>

---

# 📸 UI Preview

<p align="center">
<img src="assets/ui.png" width="95%">
</p>

---

# ✨ Features

- 🤖 AI Personal Assistant
- 📄 Chat with PDF (RAG)
- 🧠 Persistent Chat Memory
- 💬 Multi-Conversation Support
- 🛠️ Tool Calling
- 📈 Stock Analysis
- 🌦️ Weather Tool
- 🧮 Calculator
- 👨 Human Approval Workflow
- ⚡ Fast LLM Responses

---

# 🏗️ Architecture

```text
              User
                │
                ▼
       Streamlit Frontend
                │
                ▼
         LangGraph Agent
      ┌────────┼─────────┐
      │        │         │
      ▼        ▼         ▼
    RAG      Tools     Memory
      │        │         │
      ▼        ▼         ▼
 ChromaDB   Weather   SQLite
            Stock
         Calculator
```

---

# 🛠 Tech Stack

| Category | Technologies |
|-----------|--------------|
| Language | Python |
| Framework | Streamlit |
| AI | LangGraph, LangChain |
| LLM | Groq |
| RAG | ChromaDB, Google Embeddings |
| Database | SQLite |
| PDF | PyPDF |
| Tools | Calculator, Weather, Stock Analysis |

---

# 📂 Project Structure

```text
Nova-Agent/
│
├── src/
│   ├── backend.py
│   ├── rag.py
│   └── tool.py
│
├── app.py
├── requirements.txt
├── config.toml
└── README.md
```

---

# 🚀 Run Locally

```bash
git clone https://github.com/yourusername/Nova-Agent.git

cd Nova-Agent

python -m venv venv

pip install -r requirements.txt

streamlit run app.py
```

---

# 👨‍💻 Developer

**Ankit Gupta**

AI Backend Engineer | Agentic AI | RAG | LangGraph | LangChain

⭐ If you like this project, give it a star!
