# DocFlow API

DocFlow is a FastAPI backend for uploading documents, processing them asynchronously, and retrieving AI-generated summaries, invoice information, or contract metadata. PostgreSQL stores users and workflow records, MinIO stores uploaded files, and Celery workers process requests through Redis.

## Contents

- [Features and processing flow](#features-and-processing-flow)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Local development](#local-development)
- [Docker Compose](#docker-compose)
- [API walkthrough](#api-walkthrough)
- [Endpoint reference](#endpoint-reference)
- [Database migrations](#database-migrations)
- [Tests](#tests)
- [Project structure](#project-structure)
- [Troubleshooting and implementation notes](#troubleshooting-and-implementation-notes)

## Features and processing flow

- Account registration, JWT bearer authentication, profile updates, password changes, and email-based password resets.
- Document upload, per-user document/file listings, file downloads, and deletion endpoints.
- Three processing types: `DOCUMENT_SUMMARY`, `INVOICE_EXTRACTION`, and `CONTRACT_METADATA`.
- Text extraction from PDFs, DOCX documents, and OCR for JPEG, PNG, and TIFF images.
- Background processing with stored request statuses, job attempts, and extraction results.
- Interactive API documentation through FastAPI's Swagger UI and ReDoc.

```text
Client -> FastAPI -> PostgreSQL (users, documents, requests, jobs, results)
                 -> MinIO (original files)
                 -> Redis -> Celery worker
                               |-> MinIO: read file
                               |-> pypdf / python-docx / Tesseract: extract text
                               |-> OpenAI: process extracted text
                               `-> PostgreSQL: save status and result
```

An upload creates a file record, document, and processing request, then enqueues a Celery task. The usual request lifecycle is `PENDING -> QUEUED -> PROCESSING -> COMPLETED`; processing errors can set `FAILED`. `CANCELLED` is defined in the schema, but there is no cancellation endpoint.

Results are stored and returned as `{"result": "model output"}`. Invoice and contract processing currently return model-generated text, without a validated structured output schema. Extracted document text and the supplied instructions are sent to OpenAI. The model is currently hardcoded to `gpt-5.5` in [the OpenAI service](app/service/openai/service.py).

## Requirements

- **Python 3.12 or newer** for the current source: some f-strings reuse quote characters inside expressions, which older Python versions cannot parse.
- PostgreSQL (the Compose stack uses version 16).
- Redis (the Compose stack uses version 7).
- MinIO or a compatible endpoint supported by the MinIO client.
- Tesseract OCR installed wherever the Celery worker runs.
- An OpenAI API key with access to the configured model for actual processing.
- SMTP credentials/server for password reset emails.
- Docker and Docker Compose if using the included infrastructure stack.

**Docker compatibility:** the checked-in `dockerfile` currently uses `python:3.10-slim`, which conflicts with the source syntax requirement above. Use the local Python 3.12+ workflow below, or update the image's base to `python:3.12-slim` before building the application containers.

## Configuration

Run commands from the repository root. The application reads `.env` through Pydantic Settings. The checked-in [.env.example](.env.example) is incomplete: it omits required `secret_key` and `DATABASE_USER` settings, and includes an unused `REDIS_URL` entry that can trigger an extra-field validation error. Use the following complete local-development template when creating your `.env`:

```dotenv
app_name=DocFlow
secret_key=replace-with-a-random-secret
algorithm=HS256
access_token_expire_minutes=30

broker_host=redis://localhost:6379/0
broker_backend=redis://localhost:6379/1
OPENAI_API_KEY=replace-with-your-api-key

DATABASE_NAME=docflow
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5433

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=docflow
MINIO_SECURE=false

DATABASE_URL_TEST=postgresql+asyncpg://docflow_user:your_password@localhost:5432/test_docflow

reset_token_expire_minutes=60
mail_server=localhost
mail_port=587
mail_username=
mail_password=
mail_from=noreply@example.com
mail_use_tls=true
frontend_url=http://localhost:3000
```

Generate a signing secret with `python -c 'import secrets; print(secrets.token_hex(32))'` and replace the placeholder. Keep `.env` out of version control. The database and MinIO credentials above match the included local Compose services.

| Setting | Purpose / default |
| --- | --- |
| `app_name` | Required application setting; the FastAPI title is not currently wired to it. |
| `secret_key` | Required JWT signing secret. |
| `algorithm`, `access_token_expire_minutes` | JWT algorithm and token lifetime; defaults: `HS256`, `30`. |
| `broker_host`, `broker_backend` | Required Celery broker and result-backend URLs. |
| `OPENAI_API_KEY` | Required setting; a working key is needed for AI processing. |
| `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT` | Required PostgreSQL connection components, used by both the application and Alembic. |
| `MINIO_ENDPOINT` | Required `host:port`, without a URL scheme. |
| `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET` | Required storage credentials and bucket name. |
| `MINIO_SECURE` | Required boolean; use `false` for the local HTTP MinIO service. |
| `DATABASE_URL_TEST` | Required by settings, but the current test fixture overrides this value; see [Tests](#tests). |
| `reset_token_expire_minutes` | Password reset token lifetime; default: `60`. |
| `mail_server`, `mail_port` | SMTP host and port; defaults: `localhost`, `587`. |
| `mail_username`, `mail_password` | Optional SMTP authentication; defaults: empty strings. |
| `mail_from`, `mail_use_tls` | Sender and SMTP STARTTLS setting; defaults: `noreply@example.com`, `true`. |
| `frontend_url` | Base URL for the frontend's `/reset-password?token=...` page; code default: `http://localhost:8000`. No frontend is included here. |

For application containers, change these values in `.env`:

```dotenv
DATABASE_HOST=postgres
DATABASE_PORT=5432
broker_host=redis://redis:6379/0
broker_backend=redis://redis:6379/1
MINIO_ENDPOINT=minio:9000
```

The API creates the configured MinIO bucket during startup if it does not exist. Startup also checks PostgreSQL connectivity. `MINIO_BUCKET` is read directly from the process environment in the startup hook; the launch command below explicitly loads `.env` into that environment.

## Local development

1. Create `.env` using the local template above.
2. Create a Python environment and install dependencies:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Install Tesseract on the worker host:

   ```bash
   # macOS (Homebrew)
   brew install tesseract

   # Debian / Ubuntu
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```

4. Start infrastructure, then apply migrations once PostgreSQL is ready:

   ```bash
   docker compose up -d postgres redis minio
   docker compose exec postgres pg_isready -U postgres -d docflow
   alembic upgrade head
   ```

5. Start the API:

   ```bash
   uvicorn app.main:app --env-file .env --host 0.0.0.0 --port 8000 --reload
   ```

6. In a second terminal, activate the same environment and start the worker from the repository root:

   ```bash
   source .venv/bin/activate
   celery -A app.tasks.celery_app worker --loglevel=INFO
   ```

| Service | Local address |
| --- | --- |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI schema | http://localhost:8000/openapi.json |
| PostgreSQL | `localhost:5433` (container port `5432`) |
| Redis | `localhost:6379` |
| MinIO API | http://localhost:9000 |
| MinIO console | http://localhost:9001 |

Check the API with `curl http://localhost:8000/health`. The expected response is:

```json
{"status":"ok","service":"doc-flow-backend","message":"App is running"}
```

`/`, `/start`, and `/health` return the same response. These are application liveness endpoints; they do not recheck downstream services on each request.

## Docker Compose

After updating the Python base image as noted under [Requirements](#requirements), configure `.env` with the container hostnames and run:

```bash
docker compose up --build -d
docker compose logs -f api worker
```

The API entrypoint waits five seconds, runs `alembic upgrade head`, then launches Uvicorn with reload enabled. There are no readiness health checks in Compose; if PostgreSQL is still starting, the API can exit and need restarting after the database is ready:

```bash
docker compose restart api
```

The worker runs separately and must be running for queued requests to progress. This Compose configuration is for development: it bind-mounts the source tree, uses reload and debug worker logging, and publishes database/storage ports.

```bash
# Stop the stack while preserving the database and uploaded files.
docker compose down
```

PostgreSQL and MinIO use named volumes. Adding `--volumes` to `docker compose down` deletes those volumes and their stored data.

## API walkthrough

These examples use a local API and the sample PDF committed under `tests/assets/`.

### 1. Register and log in

```bash
curl -X POST http://localhost:8000/api/v1/users/signup \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Demo","last_name":"User","email":"demo@example.com","password":"ExamplePassword123!"}'

curl -X POST http://localhost:8000/api/v1/users/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'username=demo@example.com' \
  --data-urlencode 'password=ExamplePassword123!'
```

Login uses OAuth2 form fields: put the **email address in `username`**. Copy `access_token` from the response:

```bash
TOKEN='paste-access-token-here'
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Upload a document and enqueue processing

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F 'file=@tests/assets/sample-pdf-invoice.pdf;type=application/pdf' \
  -F 'processing_type=DOCUMENT_SUMMARY' \
  -F 'instructions=Summarize the key information in this document.'
```

Example response (`201 Created`; IDs vary):

```json
{"document_id":1,"processing_request_id":1,"status":"QUEUED"}
```

Use `INVOICE_EXTRACTION` or `CONTRACT_METADATA` to select the other processing modes. Both require an `instructions` field as well.

### 3. Poll status and retrieve output

Use the returned **processing request ID**:

```bash
REQUEST_ID=1
curl "http://localhost:8000/api/v1/processing-requests/status/$REQUEST_ID?processing_request_id=$REQUEST_ID" \
  -H "Authorization: Bearer $TOKEN"

# Retrieve the result after the status becomes COMPLETED.
curl "http://localhost:8000/api/v1/processing-requests/result/$REQUEST_ID?processing_request_id=$REQUEST_ID" \
  -H "Authorization: Bearer $TOKEN"
```

The current status/result handlers declare `processing_request_id` as a query parameter while the route path uses `{id}`. Supply both as shown; the query parameter selects the request. A result that is not yet available returns `404`.

### 4. Retrieve the original file

Fetch `/api/v1/documents/{document_id}` to find its `file_id`, then download using that file ID:

```bash
FILE_ID=1
curl "http://localhost:8000/api/v1/files/$FILE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  --output downloaded-document.pdf
```

## Endpoint reference

See [Swagger UI](http://localhost:8000/docs) for request schemas and interactive requests. “Bearer” below means an `Authorization: Bearer <token>` header is required by the handler.

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| GET | `/`, `/start`, `/health` | Public | Application liveness |
| POST | `/api/v1/users/signup` | Public | Register an account |
| POST | `/api/v1/users/token` | Public | Exchange email/password form for a JWT |
| GET | `/api/v1/users/me` | Bearer | Current profile |
| GET | `/api/v1/users/` | Bearer | Paginated user list |
| PATCH | `/api/v1/users/{id}` | Bearer | Update own profile |
| DELETE | `/api/v1/users/{id}` | Bearer | Delete own account |
| POST | `/api/v1/users/forgot-password` | Public | Request a reset email (`email`) |
| POST | `/api/v1/users/reset-password` | Public | Reset password (`token`, `new_password`) |
| PATCH | `/api/v1/users/me/password` | Bearer | Change password (`current_password`, `new_password`) |
| POST | `/api/v1/documents` | Bearer | Multipart upload and processing request |
| GET | `/api/v1/documents` | Bearer | List own documents |
| GET | `/api/v1/documents/{id}` | Bearer | Read document metadata |
| DELETE | `/api/v1/documents/{id}` | Bearer | Delete document |
| GET | `/api/v1/documents/{id}/jobs` | Public in current code | Job attempts; see implementation notes |
| GET | `/api/v1/files` | Bearer | List own files |
| GET | `/api/v1/files/{id}` | Bearer | Download original file |
| DELETE | `/api/v1/files/{id}` | Bearer | Soft-delete file record |
| GET | `/api/v1/processing-requests/{id}` | Bearer | Read processing request |
| GET | `/api/v1/processing-requests/status/{id}` | Bearer | Request status; also requires `processing_request_id` query parameter |
| GET | `/api/v1/processing-requests/result/{id}` | Bearer | Output; also requires `processing_request_id` query parameter |

List endpoints accept `skip` and `limit`, returning their collection plus `total`, `skip`, `limit`, and `has_more`. Defaults are `skip=0`, `limit=10`. Current bounds differ: documents allow `limit=2..50`, files `1..50`, and users `1..100`; maximum `skip` is 50 for documents/files and 100 for users.

Password reset/change schemas require at least eight characters for the new password. The reset email links to the configured frontend; the backend exposes JSON endpoints rather than a reset form.

## Database migrations

Alembic reads its database connection from the same settings as the API. For a local Python environment:

```bash
alembic current
alembic upgrade head

# After making a model change:
alembic revision --autogenerate -m "describe the schema change"
```

Review generated migrations before applying or committing them. With a running API container, use `docker compose exec api alembic current` or `docker compose exec api alembic upgrade head`. Compose's API entrypoint already applies migrations on startup.

## Tests

The suite uses pytest, AnyIO, HTTPX's ASGI transport, and a real PostgreSQL test database. File-storage calls and task submission are mocked in upload tests; these tests do not exercise real OCR or OpenAI processing.

**Use a dedicated test database:** the fixture drops and recreates all application tables at session startup, and drops them again during teardown.

The current [test fixture](tests/conftest.py) hardcodes this connection string, overriding `DATABASE_URL_TEST`:

```text
postgresql+asyncpg://docflow_user:your_password@localhost/test_docflow
```

It therefore expects PostgreSQL on port **5432**, unlike the Compose stack's host port **5433**. Before running the tests, either provision that isolated database/user on port 5432, or update the fixture's connection string to point to a dedicated test database on your chosen server. Changing `.env` alone does not change the fixture's connection.

The fixture imports the application before assigning its environment overrides, so a complete application `.env` is still required during test collection.

```bash
source .venv/bin/activate
python -m pytest -q

# Run one module:
python -m pytest tests/test_users.py -q
```

Current tests cover registration, login, profile operations, document upload/list/read/delete, and a missing-document response. They do not provide end-to-end verification of the worker pipeline or password reset email delivery.

## Project structure

```text
app/
├── main.py                    # FastAPI app, startup checks, liveness routes
├── api/v1/                    # User, document, file, processing request routes
├── core/                      # Settings and MinIO client
├── db/                        # SQLAlchemy engines, sessions, dependencies
├── models/schema.py           # Persistence models and relationships
├── service/
│   ├── auth/                  # Authentication, user operations, schemas
│   ├── document/              # Document/request operations and schemas
│   ├── file/                  # Storage operations and file schemas
│   └── openai/service.py      # AI processing calls
├── tasks/                     # Celery app, task discovery, document processing
├── utils/                     # Text extraction and email helpers
└── workers/                   # Additional worker module
migrations/                    # Alembic environment and versioned migrations
templates/email/               # Password reset email template
tests/                         # API tests, fixtures, sample PDF
alembic.ini                    # Alembic configuration
docker-compose.yml             # API, worker, PostgreSQL, Redis, MinIO
dockerfile                     # Application image (see Python version note)
entrypoint.sh                  # Migration and development API startup
requirements.txt               # Python dependencies
```

## Troubleshooting and implementation notes

| Symptom | Check |
| --- | --- |
| `SyntaxError` around an f-string | Use Python 3.12+; update the Docker base image before building. |
| Settings validation errors on startup | Supply every required setting and remove unsupported `.env` entries such as `REDIS_URL`. |
| Database connection refused | Wait for PostgreSQL and use port `5433` from the host or `postgres:5432` inside Compose. |
| MinIO connection/bucket errors | Check endpoint, credentials, and `MINIO_SECURE`; use `--env-file .env` for local Uvicorn startup. |
| Requests remain `QUEUED` | Check worker logs and confirm API/worker use the same broker and database. |
| Processing becomes `FAILED` | Check worker logs, file text extraction, Tesseract installation, API key, and model access. |
| Status/result requests return `422` | Include the `processing_request_id` query parameter as shown in the walkthrough. |
| Password reset email is not delivered | Configure a reachable SMTP server and compatible authentication/STARTTLS settings. |
| Tests cannot connect to PostgreSQL | Check the hardcoded test fixture URL and dedicated test database setup. |

The current implementation has several limits relevant to running or extending it:

- PDF extraction reads embedded text; scanned image-only PDFs are not passed through OCR.
- DOCX is accepted at upload, but its extraction helper wraps the MinIO response directly in `BytesIO` instead of reading its bytes first. DOCX processing may fail until that stream handling is corrected.
- The Celery task declares automatic retries, but its outer exception handler catches errors without re-raising them. Do not rely on automatic retries or Celery task success alone; inspect the persisted processing request status.
- The jobs endpoint has no authentication dependency, and its underlying query uses a processing request ID even though it is nested under `/documents/{id}/jobs`.
- File deletion marks the database record as deleted; it does not remove the stored MinIO object.
- Worker code logs extracted document content, and the Compose worker runs at debug level. Review logging before processing sensitive documents.

These notes describe the current code rather than guarantees of production readiness. When contributing, include migrations for model changes, update this README for configuration/API changes, and run the relevant tests against an isolated test database.
