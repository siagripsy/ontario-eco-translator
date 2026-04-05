# Project Notes

Project name: Ontario Eco-Translator

Goal:
Build an NLP RAG backend that answers user questions about NT Power electricity tariff documents in simple language.

Main stack:
- Python 3.11
- FastAPI
- SQL Server
- SQLAlchemy
- Alembic
- LangChain
- Google Gemini
- ChromaDB
- PyPDF
- Docker
- Google Cloud Run

Database name:
NTPower

Connection requirement:
The application must support two database connection modes:

1. LOCAL mode
   - Connect to a local SQL Server instance using standard SQL Server connection settings from environment variables.

2. CLOUD mode
   - Connect to Google Cloud SQL for SQL Server when deployed to Cloud Run.
   - The code must support Cloud SQL connection through environment variables and a Cloud SQL-compatible connection approach.
   - The connection logic should be selected by an environment variable such as DB_MODE=local or DB_MODE=cloud.

Important:
- Do not hardcode secrets.
- Use environment variables only.
- The code must run locally first.
- The backend must be deployment-ready for Cloud Run.
- The app should expose:
  - /health
  - /db/health
  - /documents
  - /documents/upload
  - /ask

Storage design:
- SQL Server stores structured metadata and logs
- ChromaDB stores embeddings and vector search index

Expected app behavior:
- Upload/process a tariff PDF
- Split text into chunks
- Create embeddings
- Save document and chunk metadata in SQL Server
- Save embeddings in ChromaDB
- Answer questions using retrieved context only
- Return source snippets with the answer
- Log all questions and answers in SQL Server