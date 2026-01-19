# 🔌 API Reference - Jalanamal OCR Payment Validator

Dokumentasi lengkap REST API untuk integrasi sistem validasi pembayaran.

---

## 📍 Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://api.jalanamal.com
```

---

## 🔐 Authentication

Semua endpoint (kecuali `/health` dan `/`) memerlukan API key.

### Header Required:
```http
X-API-Key: jalanamal_secure_2026_berkah
```

### Example Request:
```bash
curl -X POST "http://localhost:8000/verify-donation" \
  -H "X-API-Key: jalanamal_secure_2026_berkah" \
  -F "file=@screenshot.jpg" \
  -F "expected_amount=50000" \
  -F "bank_description=BCA"
```

---

## 📋 Endpoints

### 1. Health Check

**GET** `/health`

Endpoint untuk monitoring status sistem.

#### Request:
```http
GET /health HTTP/1.1
Host: localhost:8000
```

#### Response (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-19T20:00:00.000000",
  "version": "1.0.0",
  "dependencies": {
    "validator_module": true
  }
}
```

#### Response (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "error": "Error message here",
  "timestamp": "2026-01-19T20:00:00.000000"
}
```

#### CURL Example:
```bash
curl http://localhost:8000/health
```

---

### 2. Root Info

**GET** `/`

Mendapatkan informasi dasar API.

#### Request:
```http
GET / HTTP/1.1
Host: localhost:8000
```

#### Response (200 OK):
```json
{
  "name": "Jalanamal OCR Payment Validator API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "verify_donation": "/verify-donation (POST)"
  }
}
```

#### CURL Example:
```bash
curl http://localhost:8000/
```

---

### 3. Verify Donation ⭐

**POST** `/verify-donation`

Endpoint utama untuk memverifikasi screenshot pembayaran.

#### Request:

**Headers:**
```http
Content-Type: multipart/form-data
X-API-Key: jalanamal_secure_2026_berkah
```

**Form Data:**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `file` | File | ✅ Yes | Screenshot pembayaran | `screenshot.jpg` |
| `expected_amount` | Integer | ✅ Yes | Nominal yang diharapkan (Rupiah) | `50000` |
| `bank_description` | String | ✅ Yes | Deskripsi bank/metode pembayaran | `BCA Transfer` |

**File Constraints:**
- **Max size:** 10 MB
- **Allowed formats:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`
- **Must not be empty**

#### Response Success (200 OK):

```json
{
  "status": "VERIFIED",
  "score": 90,
  "ocr_data": {
    "raw_text": "BCA MOBILE BANKING TRANSFER BERHASIL Tanggal 19/01/2026 Pukul 20:00 WIB Rp 50.000 TUJUAN 1234567890 AN JALANAMAL REF TRX202601190001",
    "nominal": 50000,
    "bank_detected": "BCA",
    "transaction_id": "TRX202601190001",
    "ocr_noise": 0.12,
    "is_suspicious": false,
    "software_trace": null,
    "hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
  },
  "notes": [
    "✅ Platform: BCA",
    "✅ Transaction Success Confirmed",
    "✅ Amount Perfect Match: Rp 50,000",
    "✅ Unique submission",
    "✅ TX ID: TRX202601190001"
  ],
  "timestamp": "2026-01-19T20:00:00.000000"
}
```

**Status Values:**
- `VERIFIED` - Score ≥ 80, auto-approve
- `REVIEW` - Score 21-79, manual review needed
- `REJECTED` - Score ≤ 20, auto-reject

#### Response Error (401 Unauthorized):
```json
{
  "detail": "Invalid or missing API key"
}
```

#### Response Error (400 Bad Request):
```json
{
  "detail": "Invalid file type. Allowed: .jpg, .jpeg, .png, .webp, .bmp"
}
```

#### Response Error (413 Request Entity Too Large):
```json
{
  "detail": "File too large. Maximum size: 10.0MB"
}
```

#### Response Error (422 Unprocessable Entity):
```json
{
  "detail": "Expected amount must be greater than 0"
}
```

#### Response Error (500 Internal Server Error):
```json
{
  "detail": "Internal server error: <error message>"
}
```

#### CURL Example:
```bash
curl -X POST "http://localhost:8000/verify-donation" \
  -H "X-API-Key: jalanamal_secure_2026_berkah" \
  -F "file=@/path/to/screenshot.jpg" \
  -F "expected_amount=50000" \
  -F "bank_description=BCA Transfer"
```

#### Python Example:
```python
import requests

url = "http://localhost:8000/verify-donation"
headers = {
    "X-API-Key": "jalanamal_secure_2026_berkah"
}
files = {
    "file": open("screenshot.jpg", "rb")
}
data = {
    "expected_amount": 50000,
    "bank_description": "BCA Transfer"
}

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

print(f"Status: {result['status']}")
print(f"Score: {result['score']}/100")
print(f"Bank: {result['ocr_data']['bank_detected']}")
print(f"Amount: Rp {result['ocr_data']['nominal']:,}")
```

#### JavaScript Example (Node.js):
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('screenshot.jpg'));
form.append('expected_amount', '50000');
form.append('bank_description', 'BCA Transfer');

axios.post('http://localhost:8000/verify-donation', form, {
  headers: {
    ...form.getHeaders(),
    'X-API-Key': 'jalanamal_secure_2026_berkah'
  }
})
.then(response => {
  const result = response.data;
  console.log(`Status: ${result.status}`);
  console.log(`Score: ${result.score}/100`);
  console.log(`Bank: ${result.ocr_data.bank_detected}`);
  console.log(`Amount: Rp ${result.ocr_data.nominal.toLocaleString()}`);
})
.catch(error => {
  console.error('Error:', error.response?.data || error.message);
});
```

#### JavaScript Example (Browser/React):
```javascript
const uploadScreenshot = async (file, expectedAmount, bankDescription) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('expected_amount', expectedAmount);
  formData.append('bank_description', bankDescription);

  try {
    const response = await fetch('http://localhost:8000/verify-donation', {
      method: 'POST',
      headers: {
        'X-API-Key': 'jalanamal_secure_2026_berkah'
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const result = await response.json();
    console.log('Validation Result:', result);
    return result;
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};

// Usage dalam React component
const handleSubmit = async (e) => {
  e.preventDefault();
  const file = e.target.file.files[0];
  const amount = parseInt(e.target.amount.value);
  const bank = e.target.bank.value;

  const result = await uploadScreenshot(file, amount, bank);
  
  if (result.status === 'VERIFIED') {
    alert('✅ Payment verified!');
  } else if (result.status === 'REVIEW') {
    alert('⚠️ Manual review needed');
  } else {
    alert('❌ Payment rejected: ' + result.notes.join(', '));
  }
};
```

---

## 📊 Response Object Schema

### ValidationResult

```typescript
interface ValidationResult {
  status: "VERIFIED" | "REVIEW" | "REJECTED";
  score: number;  // 0-100
  ocr_data: OCRData;
  notes: string[];
  timestamp: string;  // ISO 8601 format
}
```

### OCRData

```typescript
interface OCRData {
  raw_text: string;           // Full OCR extracted text
  nominal: number;            // Detected amount in Rupiah
  bank_detected: string;      // Bank/e-wallet name or "UNKNOWN"
  transaction_id: string;     // Transaction/reference ID or "-"
  ocr_noise: number;          // Noise ratio (0.0 - 1.0)
  is_suspicious: boolean;     // True if edited
  software_trace: string | null;  // Editing software name
  hash: string;               // SHA256 hash of screenshot
}
```

---

## ⚠️ Error Handling

### Error Response Format:
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes:

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Request valid and processed |
| 400 | Bad Request | Invalid file type, empty file |
| 401 | Unauthorized | Missing/invalid API key |
| 413 | Payload Too Large | File > 10 MB |
| 422 | Unprocessable Entity | Invalid form data, amount ≤ 0 |
| 500 | Internal Server Error | OCR failure, server error |
| 503 | Service Unavailable | System unhealthy |

### Handling Errors (Python):
```python
try:
    response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()  # Raises exception for 4xx/5xx
    result = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 413:
        print("File too large")
    else:
        print(f"HTTP error: {e.response.json()['detail']}")
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
```

### Handling Errors (JavaScript):
```javascript
try {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const error = await response.json();
    
    switch (response.status) {
      case 401:
        throw new Error('Invalid API key');
      case 413:
        throw new Error('File too large (max 10MB)');
      case 422:
        throw new Error(error.detail);
      default:
        throw new Error(`Request failed: ${error.detail}`);
    }
  }
  
  return await response.json();
} catch (error) {
  console.error('API Error:', error.message);
  throw error;
}
```

---

## 🔄 Rate Limiting

**Note:** Rate limiting belum diimplementasi di versi 1.0.0

Recommended limits untuk production:
- **10 requests/minute** per IP
- **100 requests/hour** per API key
- **1000 requests/day** per API key

Implementasi rate limiting: lihat [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#security-hardening)

---

## 🧪 Testing dengan Postman

### Setup Collection:

1. **Create new collection**: "Jalanamal OCR API"

2. **Set collection variable:**
   - `base_url`: `http://localhost:8000`
   - `api_key`: `jalanamal_secure_2026_berkah`

3. **Create requests:**

#### Request 1: Health Check
```
GET {{base_url}}/health
```

#### Request 2: Verify Donation (Success Case)
```
POST {{base_url}}/verify-donation
Headers:
  X-API-Key: {{api_key}}
Body (form-data):
  file: [select screenshot.jpg]
  expected_amount: 50000
  bank_description: BCA Transfer
```

#### Request 3: Verify Donation (Invalid API Key)
```
POST {{base_url}}/verify-donation
Headers:
  X-API-Key: invalid_key
Body (form-data):
  file: [select screenshot.jpg]
  expected_amount: 50000
  bank_description: BCA
```

---

## 📈 Best Practices

### 1. Retry Logic

Implement exponential backoff untuk network errors:

```python
import time

def verify_with_retry(file_path, amount, bank, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
            time.sleep(wait_time)
```

### 2. Timeout Setting

Set reasonable timeout untuk avoid hanging:

```python
response = requests.post(
    url,
    headers=headers,
    files=files,
    data=data,
    timeout=30  # 30 seconds timeout
)
```

### 3. File Validation (Client-Side)

Validasi sebelum upload untuk better UX:

```javascript
const validateFile = (file) => {
  const maxSize = 10 * 1024 * 1024; // 10 MB
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
  
  if (file.size > maxSize) {
    throw new Error('File terlalu besar (max 10MB)');
  }
  
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Format file tidak didukung (gunakan JPG/PNG/WEBP)');
  }
  
  return true;
};
```

### 4. Progress Tracking

Tampilkan progress untuk better UX:

```javascript
const uploadWithProgress = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('expected_amount', amount);
  formData.append('bank_description', bank);
  
  const xhr = new XMLHttpRequest();
  
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percentComplete = (e.loaded / e.total) * 100;
      onProgress(percentComplete);
    }
  });
  
  return new Promise((resolve, reject) => {
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(xhr.responseText));
      }
    });
    
    xhr.addEventListener('error', () => reject(new Error('Upload failed')));
    
    xhr.open('POST', url);
    xhr.setRequestHeader('X-API-Key', apiKey);
    xhr.send(formData);
  });
};
```

---

## 🔔 Webhooks (Future Feature)

Planned untuk versi 2.0:

```json
POST https://your-app.com/webhook/validation-result
{
  "event": "validation.completed",
  "data": {
    "validation_id": "val_12345",
    "status": "VERIFIED",
    "score": 90,
    "timestamp": "2026-01-19T20:00:00"
  }
}
```

---

## 📝 Changelog

### v1.0.0 (2026-01-19)
- Initial API release
- POST /verify-donation endpoint
- GET /health endpoint
- GET / (root) endpoint
- API key authentication
- Multi-bank support (13 platforms)
- Anti-fraud validation
- Audit logging

---

## 🆘 Support

- 📖 [Full Documentation](README.md)
- 👨‍💻 [Developer Guide](DEVELOPER_GUIDE.md)
- 🌐 Swagger UI: http://localhost:8000/docs
- 📧 Email: support@jalanamal.com

---

**Jalanamal OCR Payment Validator API v1.0.0**

*Made with ❤️ for seamless payment validation*
