# 👨‍💻 Developer Guide - Jalanamal OCR Payment Validator

Panduan teknis lengkap untuk developer yang ingin memahami, memodifikasi, atau mengembangkan sistem OCR Payment Validator.

---

## 📐 Arsitektur Sistem

```mermaid
graph TB
    A[User Upload Screenshot] --> B[Frontend Next.js]
    B --> C[FastAPI Backend]
    C --> D[Image Preprocessing]
    D --> E[EasyOCR Engine]
    E --> F[Bank Detection]
    F --> G[Validation Engine]
    G --> H[Anti-Fraud Checks]
    H --> I[Scoring Algorithm]
    I --> J{Score?}
    J -->|≥80| K[VERIFIED]
    J -->|21-79| L[REVIEW]
    J -->|≤20| M[REJECTED]
    K --> N[Audit Log]
    L --> N
    M --> N
    N --> O[Response to Frontend]
```

---

## 🔧 Komponen Utama

### 1. Backend Components

#### **1.1 API Layer (`api.py`)**

**Responsibilities:**
- HTTP request handling
- File upload validation
- API authentication
- CORS management
- Error handling and logging

**Key Functions:**

```python
@app.post("/verify-donation")
async def verify_donation(
    x_api_key: str,
    file: UploadFile,
    expected_amount: int,
    bank_description: str
)
```

**Flow:**
1. Validate API key
2. Validate file (type, size)
3. Save temporary file
4. Call OCR extraction
5. Call validation
6. Log result
7. Return response
8. Cleanup temp file

#### **1.2 Validator Module (`validator.py`)**

**Responsibilities:**
- Image preprocessing
- OCR execution
- Bank/e-wallet detection
- Transaction validation
- Anti-fraud checks

**Key Classes/Functions:**

##### `get_ocr_reader() -> easyocr.Reader`
Singleton pattern untuk OCR reader (avoid reload overhead).

##### `preprocess(path: str) -> str`
Optimized preprocessing untuk mobile screenshots:
- Upscaling jika gambar kecil
- Grayscale conversion
- Gaussian blur (fast alternative to denoise)
- CLAHE enhancement

##### `detect_bank(text: str) -> str`
Flexible bank detection dengan scoring:
- Brand keywords (+10)
- Success indicators (+5)
- Amount keywords (+2)
- Forbidden words (-20)

##### `clean_currency(text: str) -> int`
Smart currency parser yang handle:
- Indonesian format: `10.546,00`
- International format: `10,546.00`
- Mixed format
- Thousand vs decimal separator detection

##### `extract_data_from_image(path: str) -> Dict`
Main OCR function yang return:
```python
{
    "raw_text": str,          # Full OCR text
    "nominal": int,           # Extracted amount
    "bank_detected": str,     # Bank/e-wallet name
    "transaction_id": str,    # Transaction ID
    "ocr_noise": float,       # Noise ratio (0-1)
    "is_suspicious": bool,    # Edit detection
    "software_trace": str,    # Editing software name
    "hash": str               # SHA256 hash
}
```

##### `validate_donation(ocr: Dict, mutation: Dict) -> Tuple[int, List[str]]`
Core validation dengan 7 checks:
1. Edit detection (instant reject)
2. Template detection (instant reject)
3. Bank detection (±20 points)
4. Success indicator (±20 points)
5. Amount validation (0-30 points)
6. Replay protection (instant reject or +10)
7. Transaction ID (+10 points)

Returns: `(score, notes)`

---

### 2. Frontend Components

#### **2.1 Main Upload Component**

Location: `frontend/components/`

**Features:**
- Drag & drop file upload
- Preview image
- Form validation
- API integration
- Result display

**State Management:**
```typescript
interface ValidationResult {
  status: 'VERIFIED' | 'REVIEW' | 'REJECTED';
  score: number;
  ocr_data: OCRData;
  notes: string[];
  timestamp: string;
}
```

---

## 🧪 Testing Guide

### Unit Tests (Backend)

Create `backend-ocr/test_validator.py`:

```python
import pytest
from validator import clean_currency, detect_bank, validate_donation

def test_clean_currency_indonesian():
    assert clean_currency("Rp 10.546,00") == 10546
    assert clean_currency("10.546") == 10546
    assert clean_currency("Rp10.546") == 10546

def test_clean_currency_international():
    assert clean_currency("Rp 10,546.00") == 10546
    assert clean_currency("$10,546") == 10546

def test_detect_bank():
    text = "BCA MOBILE TRANSFER BERHASIL Rp 50.000"
    assert detect_bank(text) == "BCA"
    
    text2 = "GOPAY TRANSFER SELESAI"
    assert detect_bank(text2) == "GOPAY"

def test_validate_donation_success():
    ocr = {
        "nominal": 50000,
        "bank_detected": "BCA",
        "transaction_id": "TRX123",
        "is_suspicious": False,
        "ocr_noise": 0.1,
        "hash": "abc123"
    }
    mutation = {"amount": 50000, "description": "BCA"}
    
    score, notes = validate_donation(ocr, mutation)
    assert score >= 80
    assert any("Perfect Match" in note for note in notes)

def test_validate_donation_edited():
    ocr = {
        "nominal": 50000,
        "is_suspicious": True,
        "software_trace": "Adobe Photoshop"
    }
    mutation = {"amount": 50000}
    
    score, notes = validate_donation(ocr, mutation)
    assert score == 0
    assert "EDITED" in notes[0]
```

Run tests:
```bash
pytest backend-ocr/test_validator.py -v
```

### Integration Tests

Create `backend-ocr/test_api.py`:

```python
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_verify_donation_no_api_key():
    response = client.post("/verify-donation")
    assert response.status_code == 401

def test_verify_donation_success():
    with open("test_screenshot.jpg", "rb") as f:
        response = client.post(
            "/verify-donation",
            headers={"X-API-Key": "jalanamal_secure_2026_berkah"},
            files={"file": f},
            data={
                "expected_amount": 50000,
                "bank_description": "BCA"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "score" in data
```

---

## 🔍 Debugging Tips

### 1. Enable Debug Logging

```python
# Di validator.py atau api.py
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Save Preprocessed Images

```python
# Di preprocess() function
DEBUG_SAVE = True

if DEBUG_SAVE:
    cv2.imwrite(f"debug/{os.path.basename(path)}", enhanced)
```

### 3. Print OCR Raw Results

```python
# Di extract_data_from_image()
logger.debug(f"OCR Raw Results:")
for bbox, text, conf in ocr_raw:
    logger.debug(f"  {text} (confidence: {conf:.2f})")
```

### 4. Test Individual Components

```python
# Test preprocessing
from validator import preprocess
preprocessed = preprocess("test.jpg")

# Test OCR
from validator import get_ocr_reader
reader = get_ocr_reader()
result = reader.readtext("test.jpg")
print(result)

# Test bank detection
from validator import detect_bank
bank = detect_bank("BCA MOBILE BERHASIL Rp 50.000")
print(bank)
```

---

## 🚀 Optimization Tips

### 1. OCR Performance

**Current**: ~3-5 seconds per image

**Optimizations:**
```python
# Use GPU if available
reader = easyocr.Reader(['id', 'en'], gpu=True)

# Reduce languages if not needed
reader = easyocr.Reader(['id'], gpu=False)  # Faster

# Limit OCR area (if screenshot format is consistent)
result = reader.readtext(
    image,
    width_ths=0.7,  # Reduce width threshold
    paragraph=False,
    min_size=20     # Ignore small text
)
```

### 2. Image Preprocessing

**Current**: Gaussian blur (fast)

**Alternative** (better quality, slower):
```python
# Replace Gaussian with bilateral filter
blurred = cv2.bilateralFilter(gray, 9, 75, 75)

# Or use fastNlMeansDenoising (slowest but best)
denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
```

### 3. Caching

Implement Redis cache untuk prevent duplicate processing:

```python
import redis
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(image_hash: str):
    cached = redis_client.get(f"ocr:{image_hash}")
    if cached:
        return json.loads(cached)
    return None

def cache_result(image_hash: str, result: dict):
    redis_client.setex(
        f"ocr:{image_hash}",
        3600,  # 1 hour TTL
        json.dumps(result)
    )
```

---

## 🔐 Security Hardening

### 1. API Key Rotation

```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
API_SECRET = os.getenv("API_SECRET")

# Implement key rotation
VALID_API_KEYS = os.getenv("API_KEYS", "").split(",")

def verify_api_key(key: str) -> bool:
    return key in VALID_API_KEYS
```

### 2. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/verify-donation")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def verify_donation(...):
    ...
```

### 3. Input Sanitization

```python
import re

def sanitize_filename(filename: str) -> str:
    # Remove path traversal attempts
    filename = os.path.basename(filename)
    # Remove special characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename

# Usage
safe_filename = sanitize_filename(file.filename)
temp_path = f"temp_{safe_filename}"
```

### 4. HTTPS Only (Production)

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 📊 Database Integration

### Option 1: SQLite (Simple)

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('jalanamal.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                bank TEXT,
                expected_amount INTEGER,
                actual_amount INTEGER,
                score INTEGER,
                status TEXT,
                notes TEXT,
                image_hash TEXT UNIQUE
            )
        ''')
        conn.commit()

def save_validation(data: dict):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO validations 
            (timestamp, bank, expected_amount, actual_amount, score, status, notes, image_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            data['bank'],
            data['expected'],
            data['actual'],
            data['score'],
            data['status'],
            ' | '.join(data['notes']),
            data['hash']
        ))
        conn.commit()
```

### Option 2: PostgreSQL (Production)

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/jalanamal")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Validation(Base):
    __tablename__ = "validations"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    bank = Column(String)
    expected_amount = Column(Integer)
    actual_amount = Column(Integer)
    score = Column(Integer)
    status = Column(String)
    notes = Column(String)
    image_hash = Column(String, unique=True)

Base.metadata.create_all(engine)

def save_validation(data: dict):
    session = SessionLocal()
    validation = Validation(**data)
    session.add(validation)
    session.commit()
    session.close()
```

---

## 🎨 Frontend Customization

### Custom Styling

```typescript
// components/ValidationCard.tsx
interface ValidationCardProps {
  result: ValidationResult;
}

export function ValidationCard({ result }: ValidationCardProps) {
  const statusConfig = {
    VERIFIED: {
      color: 'green',
      icon: '✅',
      title: 'Terverifikasi'
    },
    REVIEW: {
      color: 'yellow',
      icon: '⚠️',
      title: 'Perlu Review'
    },
    REJECTED: {
      color: 'red',
      icon: '❌',
      title: 'Ditolak'
    }
  };
  
  const config = statusConfig[result.status];
  
  return (
    <div className={`border-l-4 border-${config.color}-500 p-4`}>
      <h3 className="flex items-center gap-2">
        <span>{config.icon}</span>
        {config.title}
      </h3>
      <p>Score: {result.score}/100</p>
      <p>Bank: {result.ocr_data.bank_detected}</p>
      <p>Nominal: Rp {result.ocr_data.nominal.toLocaleString('id-ID')}</p>
      
      <div className="mt-4">
        <h4>Validation Notes:</h4>
        <ul>
          {result.notes.map((note, i) => (
            <li key={i}>{note}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

## 🌐 Deployment

### Docker Setup

**Dockerfile (Backend):**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend-ocr
    ports:
      - "8000:8000"
    environment:
      - API_SECRET=${API_SECRET}
    volumes:
      - ./backend-ocr:/app
    restart: unless-stopped
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

---

## 📈 Monitoring & Logging

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

validation_counter = Counter(
    'validation_total',
    'Total validations',
    ['status', 'bank']
)

validation_duration = Histogram(
    'validation_duration_seconds',
    'Validation duration'
)

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

@app.post("/verify-donation")
async def verify_donation(...):
    with validation_duration.time():
        # ... validation logic ...
        validation_counter.labels(
            status=validation_status,
            bank=ocr_result['bank_detected']
        ).inc()
```

### Grafana Dashboard

Metrics to track:
- Total validations per hour
- Success rate (VERIFIED %)
- Average score
- Bank distribution
- API response time
- Error rate

---

## 🛠 Common Modifications

### 1. Add New Bank

```python
# In validator.py BANK_BEHAVIORS dict
"SEABANK": {
    "brand_keywords": ["SEABANK", "SEA BANK"],
    "success_indicators": ["BERHASIL", "SUCCESS"],
    "forbidden": ["INVOICE"],
    "amount_keywords": ["RP", "TOTAL"],
    "id_pattern": r"(REF|TRANSACTION\s*ID)[:\s]*([A-Z0-9]+)"
}
```

### 2. Adjust Scoring Weights

```python
# In validate_donation() function

# Increase bank detection importance
if bank != "UNKNOWN":
    score += 30  # Changed from 20

# Decrease transaction ID importance
if ocr["transaction_id"] != "-":
    score += 5  # Changed from 10
```

### 3. Custom Validation Rules

```python
# Add custom check in validate_donation()

# Check 8: Minimum amount requirement
if ocr["nominal"] < 10000:
    score -= 15
    reasons.append("⚠️ Amount below minimum (Rp 10,000)")
```

---

## 📚 Additional Resources

- **EasyOCR Docs**: https://github.com/JaidedAI/EasyOCR
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenCV Tutorials**: https://docs.opencv.org/
- **Next.js Docs**: https://nextjs.org/docs

---

**Happy Coding! 🚀**
