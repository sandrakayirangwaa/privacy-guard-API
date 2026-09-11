# The Personal Privacy Guard API

This system automatically detects and masks sensitive identifiers (PII) such as emails, phone numbers, and credit cards from unstructured text before it enters external environments or public LLM pipelines, while maintaining a secure local decryption mechanism.

## Key Features

* Utilizes optimized, pre-compiled regular expressions for lightning-fast pattern validation and text masking under 2 milliseconds.
* Leverages symmetric AES-256 encryption (`cryptography.fernet`) to transform raw sensitive metrics into unreadable binary blocks before persisting to disk.
* Seamlessly restores tokenized placeholders (`[EMAIL_23fa9]`) back to their authenticated clear-text values via a secure `/desanitize` lookup.

## Architecture Flow

```text
[ Incoming Raw Text ] ──> ( FastAPI Input Schema Validation )
                                       │
                                       ▼
                     ( High-Speed Pattern Masking Engine )
                                       │
             ┌─────────────────────────┴─────────────────────────┐
             ▼                                                   ▼
     [ Sanitized Output ]                                [ Secure Tokens Mapping ]
"Please call [EMAIL_23fa9]"                                     │
             │                                                   ▼
             │                                        ( Fernet Key Encryption )
             ▼                                                   │
  ( Safe for Public LLMs )                                       ▼
                                                       [ PostgreSQL Vault Storage ]
```

## Project Structure

```text
privacy-guard/
│
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application routing & lifecycle hooks
│   ├── database.py      # PostgreSQL async configuration & encryption routines
│   ├── engine.py        # Optimized token parsing & regex mapping logic
│   ├── models.py        # SQLAlchemy relational schemas
│   └── schemas.py       # Pydantic rigorous input/output validation models
│
├── .env                 # Secret application credentials (ignored by Git)
├── .gitignore           # Keeps dependency baselines out of source control
└── requirements.txt     # Managed Python environment dependencies
```

## Local Setup & Installation

### 1. Clone & Set Up Environment
Ensure your terminal environment is active:
```bash
cd privacy-guard
python3 -m venv privacy
source privacy/bin/activate 
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```text
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/privacy_guard_db
ENCRYPTION_KEY=your_32_byte_fernet_compatible_base64_key
```

### 4. Initialize Database & Run Server
Ensure your local PostgreSQL service is running and the targeted database exists. Then boot the development server:
```bash
uvicorn app.main:app --reload
```
The server will initialize tables automatically and host live documentation at `http://127.0.0`.

## API Documentation

### `POST /sanitize`
Ingests unstructured text, masks strings matching PII patterns, and securely records encrypted values.

* **Payload Example:**
  ```json
  {
    "text": "Please reach out to me at sandra.dev@gmail.com or call 555-123-4567."
  }
  ```
* **Response Example (201 Created):**
  ```json
  {
    "original_text": "Please reach out to me at sandra.dev@gmail.com or call 555-123-4567.",
    "sanitized_text": "Please reach out to me at [EMAIL_23fa9] or call [PHONE_dcc74]."
  }
  ```

### `POST /desanitize`
Scans token placeholders from a processed text block, handles secure target decryption, and swaps original entities back into position.

* **Payload Example:**
  ```json
  {
    "text": "Please reach out to me at [EMAIL_23fa9] or call [PHONE_dcc74]."
  }
  ```
* **Response Example (200 OK):**
  ```json
  {
    "restored_text": "Please reach out to me at sandra.dev@gmail.com or call 555-123-4567."
  }
  ```
