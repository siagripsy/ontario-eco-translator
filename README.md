# Ontario-Eco-Translator

Production-style FastAPI backend for Retrieval-Augmented Generation over NT Power tariff PDFs. The API ingests tariff documents, stores metadata in SQL Server, stores embeddings in ChromaDB, and answers questions in simple plain English using Gemini with retrieved context only.

## Stack

- Python 3.11
- FastAPI
- SQL Server with SQLAlchemy ORM
- Alembic
- LangChain
- Google Gemini for embeddings and chat
- ChromaDB
- PyPDF
- Docker
- Google Cloud Run

## Project Structure

```text
app/
  api/routes/         FastAPI route handlers
  core/               settings and logging
  db/                 engine/session setup
  models/             SQLAlchemy ORM models
  prompts/            reusable LLM prompt templates
  repositories/       persistence helpers
  schemas/            request/response models
  services/           ingestion, chunking, vector, and QA logic
  utils/              small shared helpers
alembic/              migration environment and revisions
chroma_db/            local Chroma persistence
data/uploads/         uploaded PDFs
tests/                API smoke tests
```

## Environment Variables

Copy `.env.example` to `.env` and set values.

### Shared

- `DB_NAME=NTPower`
- `DB_USER`
- `DB_PASSWORD`
- `GOOGLE_API_KEY`
- `GEMINI_CHAT_MODEL`
- `GEMINI_EMBEDDING_MODEL`
- `CHROMA_PERSIST_DIR`
- `UPLOADS_DIR`

### Local SQL Server mode

```env
DB_MODE=local
DB_HOST=localhost
DB_PORT=1433
DB_NAME=NTPower
DB_USER=sa
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 18 for SQL Server
```

### Cloud SQL for SQL Server mode

```env
DB_MODE=cloud
CLOUD_SQL_CONNECTION_NAME=project:region:instance
DB_NAME=NTPower
DB_USER=sqlserver_user
DB_PASSWORD=strong_password
DB_DRIVER=ODBC Driver 18 for SQL Server
CLOUD_SQL_IP_TYPE=private
```

Notes:

- The application selects the SQLAlchemy engine based on `DB_MODE`.
- `local` mode uses `pyodbc` and a standard SQL Server connection string.
- `cloud` mode uses the Cloud SQL Python Connector with `pytds`, which is a clean fit for Cloud Run and avoids hardcoding hostnames.
- For Alembic in `cloud` mode, set `ALEMBIC_DATABASE_URL` to a direct SQL Server URL that your migration environment can reach.
- With the current `langchain_google_genai` integration in this project, use `GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001`.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Create the `NTPower` database in SQL Server, then run migrations:

```bash
alembic upgrade head
```

Start the API locally:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Demo UI

A polished single-page demo frontend is available in `frontend/`.

Setup:

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Default frontend environment:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

With the FastAPI backend running, open the Vite URL shown in the terminal, usually:

```text
http://127.0.0.1:5173
```

You can also run the compatibility launcher:

```bash
python appmain.py
```

## Alembic Commands

```bash
alembic revision -m "describe change"
alembic upgrade head
alembic downgrade -1
```

## API Endpoints

- `GET /health`
- `GET /db/health`
- `GET /documents`
- `POST /documents/upload`
- `POST /ask`

### curl Examples

Health:

```bash
curl http://localhost:8000/health
```

Database health:

```bash
curl http://localhost:8000/db/health
```

Upload a tariff PDF:

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ntpower-tariff.pdf;type=application/pdf"
```

Ask a question:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is the monthly service charge for residential customers?\"}"
```

## Processing Flow

1. Upload a PDF tariff document.
2. Extract page text with PyPDF.
3. Split text into overlapping chunks.
4. Save document and chunk metadata in SQL Server.
5. Create Gemini embeddings and store them in ChromaDB.
6. Retrieve relevant chunks for questions.
7. Generate a plain-English answer using only retrieved context.
8. Log the question, answer, and retrieved snippets in `query_logs`.

## Docker

Build the image:

```bash
docker build -t ontario-eco-translator .
```

Run the container locally:

```bash
docker run --rm -p 8000:8080 --env-file .env ontario-eco-translator
```

For local Docker testing against SQL Server running on your host machine, use:

```env
DB_MODE=local
DB_HOST=host.docker.internal
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server
```

Notes:

- `host.docker.internal` lets the container reach SQL Server running on your local machine.
- The Docker image installs `msodbcsql18`, so `DB_DRIVER` should be `ODBC Driver 18 for SQL Server`.
- After changing the Dockerfile, rebuild the image before testing again.

## Cloud Run Deployment

For Cloud Run, use `DB_MODE=cloud` and the Cloud SQL Python Connector path that is already implemented in the backend.

Recommended runtime env template:

```bash
copy .env.cloudrun.example .env.cloudrun
```

Important Cloud Run values:

```env
DB_MODE=cloud
CLOUD_SQL_CONNECTION_NAME=your-project:your-region:your-instance
CLOUD_SQL_IP_TYPE=public
DB_NAME=NTPower
DB_USER=your_sqlserver_user
DB_PASSWORD=your_sqlserver_password
GOOGLE_API_KEY=your_google_api_key
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
CHROMA_PERSIST_DIR=/tmp/chroma_db
UPLOADS_DIR=/tmp/uploads
PORT=8080
```

Why `/tmp`:

- Cloud Run containers have ephemeral local storage.
- `uploads` and local Chroma persistence should use `/tmp` for demo deployment unless you move them to persistent managed storage later.

Typical deploy flow:

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev

gcloud artifacts repositories create ontario-eco-translator ^
  --repository-format=docker ^
  --location=us-central1

docker build -t us-central1-docker.pkg.dev/PROJECT_ID/ontario-eco-translator/app:latest .

docker push us-central1-docker.pkg.dev/PROJECT_ID/ontario-eco-translator/app:latest

gcloud run deploy ontario-eco-translator ^
  --image us-central1-docker.pkg.dev/PROJECT_ID/ontario-eco-translator/app:latest ^
  --region us-central1 ^
  --platform managed ^
  --allow-unauthenticated ^
  --port 8080 ^
  --service-account YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com ^
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME ^
  --env-vars-file .env.cloudrun
```

Required Google Cloud setup:

- Enable Cloud Run Admin API, Artifact Registry API, Cloud Build API, and Cloud SQL Admin API.
- Grant the Cloud Run service account the `Cloud SQL Client` role.
- Use a Cloud SQL for SQL Server instance in the same region as Cloud Run when possible.

## Cloud Run Deployment Notes

- The container listens on `PORT` and binds to `0.0.0.0`.
- Configure the Cloud Run service with the required environment variables from `.env.example`.
- Attach the Cloud SQL instance and grant the service account the `Cloud SQL Client` role.
- For SQL Server on Cloud Run, this project is prepared to use the Cloud SQL Python Connector in `DB_MODE=cloud`.
- Keep `CLOUD_SQL_CONNECTION_NAME` set to the exact instance connection name.
- Use a persistent or mounted volume strategy only if you need Chroma persistence beyond a single container lifecycle. For production, many teams move vector data to a managed vector store later.

## Testing

```bash
pytest
```
