<div align="center">

![Nunudev Studio](assets/Logo.png)

</div>

---

# 🔍 Jalanamal OCR Payment Validator

Sistem otomatis untuk validasi screenshot pembayaran/donasi menggunakan teknologi OCR (Optical Character Recognition) dan AI untuk mendeteksi keaslian transaksi.

**Developed by [Nunudev Studio](https://github.com/NunudevStudio)** 🚀

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Teknologi](#-teknologi)
- [Instalasi](#-instalasi)
- [Cara Penggunaan](#-cara-penggunaan)
- [API Documentation](#-api-documentation)
- [Konfigurasi](#-konfigurasi)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Fitur Utama

### 1. **Multi-Bank/E-Wallet Detection**
Mendukung deteksi otomatis dari berbagai platform pembayaran:

#### **Perbankan:**
- BCA (Bank Central Asia)
- BRI (Bank Rakyat Indonesia)
- Mandiri / Livin'
- BSI (Bank Syariah Indonesia)
- BNI (Bank Negara Indonesia)
- CIMB Niaga
- Permata Bank
- BTN (Bank Tabungan Negara)

#### **E-Wallet:**
- DANA
- GoPay
- OVO
- ShopeePay
- LinkAja

### 2. **OCR Engine Canggih**
- **Preprocessing Otomatis**: Meningkatkan kualitas gambar sebelum OCR
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - Gaussian Blur untuk noise reduction
  - Upscaling untuk gambar kecil
- **Multi-Language Support**: Indonesia & English
- **High Accuracy**: Optimized untuk screenshot mobile banking

### 3. **Validasi Nominal Cerdas**
- **Format Indonesia**: Mendukung format `10.546,00` (titik = ribuan, koma = desimal)
- **Format International**: Mendukung format `10,546.00`
- **Tolerance Mode**: Menerima perbedaan kecil untuk kode unik (±999)
- **Range Filtering**: Otomatis filter nominal tidak wajar (1rb - 1M)

### 4. **Anti-Fraud System**

#### **4.1 Edit Detection**
Mendeteksi apakah gambar telah diedit menggunakan:
- Adobe Photoshop
- Canva
- GIMP
- PicsArt
- Dan software editing lainnya

#### **4.2 Template Detection**
Mendeteksi screenshot palsu dari template dengan menganalisis:
- OCR confidence score
- Noise ratio (gambar terlalu bersih = suspicious)

#### **4.3 Replay Attack Protection**
- Hash-based deduplication
- Mencegah screenshot yang sama di-submit berulang kali
- File: `used_hashes.txt`

#### **4.4 Forbidden Content Detection**
Menolak screenshot yang bukan transfer bank:
- Invoice marketplace
- Order ID belanja online
- Screenshot QRIS
- Dan konten non-transfer lainnya

### 5. **Smart Validation Scoring**

Sistem scoring 0-100 berdasarkan:

| Kriteria | Bobot |
|----------|-------|
| Platform Detection (Bank/E-wallet) | 20 poin |
| Success Indicator ("Berhasil") | 20 poin |
| Amount Match (Perfect) | 30 poin |
| Amount Match (±tolerance) | 20 poin |
| Unique Submission | 10 poin |
| Transaction ID Found | 10 poin |

**Status Keputusan:**
- **Score ≥ 80**: ✅ **VERIFIED** - Auto-approve
- **Score 21-79**: ⚠️ **REVIEW** - Manual review required
- **Score ≤ 20**: ❌ **REJECTED** - Auto-reject

### 6. **Audit Logging**
Setiap validasi dicatat ke `audit_log.csv` dengan informasi:
- Timestamp
- Bank/Platform terdeteksi
- Nominal expected vs actual
- Score validasi
- Status (VERIFIED/REVIEW/REJECTED)
- Detail notes

### 7. **REST API FastAPI**
- **Endpoint Terstruktur**: `/verify-donation`
- **API Key Authentication**: Keamanan akses
- **CORS Support**: Integrasi frontend mudah
- **Health Check**: Monitoring endpoint `/health`
- **Error Handling**: Response error yang informatif

---

## 🛠 Teknologi

### Backend
- **Python 3.8+**
- **FastAPI**: Modern web framework
- **EasyOCR**: OCR engine
- **OpenCV**: Image processing
- **Pillow**: Image metadata extraction

### Frontend
- **Next.js 14+**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Lucide Icons**: Icon library

---

## 📦 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd OCR_TEST
```

### 2. Setup Backend

```bash
cd backend-ocr

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup .env file
copy .env.example .env
# Edit .env dan isi API_SECRET
```

**requirements.txt:**
```
fastapi
uvicorn[standard]
python-multipart
easyocr
opencv-python
Pillow
python-dotenv
```

### 3. Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Setup environment variables
# Buat file .env.local dan isi:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🚀 Cara Penggunaan

### Menjalankan Backend

```bash
cd backend-ocr
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

API akan berjalan di: `http://localhost:8000`

**Swagger Docs**: `http://localhost:8000/docs`

### Menjalankan Frontend

```bash
cd frontend
npm run dev
```

Frontend akan berjalan di: `http://localhost:3000`

### Workflow Penggunaan

1. **User Upload Screenshot**
   - Buka halaman frontend
   - Upload screenshot pembayaran
   - Input nominal yang diharapkan
   - Input deskripsi bank (opsional)

2. **Sistem Memproses**
   - Preprocessing gambar
   - OCR extraction
   - Bank detection
   - Validation checks

3. **Hasil Validasi**
   - Status: VERIFIED / REVIEW / REJECTED
   - Score (0-100)
   - Detail OCR data
   - Validation notes

4. **Admin Action**
   - VERIFIED: Auto-approve
   - REVIEW: Manual check required
   - REJECTED: Auto-reject + notify user

---

## 📖 API Documentation

### POST `/verify-donation`

Endpoint untuk verifikasi screenshot donasi/pembayaran.

#### Headers
```
X-API-Key: jalanamal_secure_2026_berkah
Content-Type: multipart/form-data
```

#### Request Body (Form Data)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | ✅ | Screenshot pembayaran (JPG/PNG/WEBP) |
| `expected_amount` | Integer | ✅ | Nominal yang diharapkan (Rupiah) |
| `bank_description` | String | ✅ | Deskripsi bank/metode pembayaran |

#### Response Success (200)

```json
{
  "status": "VERIFIED",
  "score": 90,
  "ocr_data": {
    "raw_text": "BCA MOBILE TRANSFER BERHASIL Rp 50.000...",
    "nominal": 50000,
    "bank_detected": "BCA",
    "transaction_id": "TRX123456789",
    "ocr_noise": 0.12,
    "is_suspicious": false,
    "software_trace": null,
    "hash": "abc123..."
  },
  "notes": [
    "✅ Platform: BCA",
    "✅ Transaction Success Confirmed",
    "✅ Amount Perfect Match: Rp 50,000",
    "✅ Unique submission",
    "✅ TX ID: TRX123456789"
  ],
  "timestamp": "2026-01-19T20:00:00"
}
```

#### Response Error (4xx/5xx)

```json
{
  "detail": "Error message here"
}
```

### GET `/health`

Health check endpoint untuk monitoring.

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2026-01-19T20:00:00",
  "version": "1.0.0",
  "dependencies": {
    "validator_module": true
  }
}
```

### GET `/`

Root endpoint dengan informasi API.

---

## ⚙️ Konfigurasi

### Backend Configuration (`backend-ocr/api.py`)

```python
# API Security
API_SECRET = "jalanamal_secure_2026_berkah"  # Ganti di production!

# File Limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
```

### Validation Thresholds (`backend-ocr/validator.py`)

```python
# Scoring Thresholds
VERIFIED_THRESHOLD = 80   # Auto-approve
REJECTED_THRESHOLD = 20   # Auto-reject

# Amount Tolerance
AMOUNT_TOLERANCE = 999    # Kode unik ±999

# Valid Amount Range
MIN_AMOUNT = 1000         # Minimal Rp 1.000
MAX_AMOUNT = 1_000_000_000  # Maksimal Rp 1M
```

### Menambah Bank/E-Wallet Baru

Edit `BANK_BEHAVIORS` di `validator.py`:

```python
"NAMA_BANK": {
    "brand_keywords": ["KEYWORD1", "KEYWORD2"],
    "success_indicators": ["BERHASIL", "SUCCESS"],
    "forbidden": ["INVOICE", "ORDER"],
    "amount_keywords": ["RP", "JUMLAH"],
    "id_pattern": r"(REF|NO)[:\s]*([A-Z0-9]+)"
}
```

---

## 🐛 Troubleshooting

### Backend Issues

#### 1. OCR Tidak Akurat
**Problem**: Nominal tidak terdeteksi atau salah

**Solutions:**
- Pastikan screenshot jelas (tidak blur)
- Screenshot full screen (bukan crop)
- Cek format angka (10.546 vs 10,546)
- Tingkatkan resolusi gambar

#### 2. Bank Tidak Terdeteksi
**Problem**: Bank detected = "UNKNOWN"

**Solutions:**
- Tambahkan brand keywords di `BANK_BEHAVIORS`
- Cek apakah ada kata "BERHASIL" di screenshot
- Pastikan bukan screenshot invoice/belanja

#### 3. False Positive pada Edit Detection
**Problem**: Screenshot asli dari HP ditandai sebagai "EDITED"

**Solutions:**
- Screenshot langsung dari HP (jangan download ulang)
- Jangan crop/edit gambar
- Gunakan screenshot bawaan OS

### Frontend Issues

#### 1. CORS Error
**Problem**: `Access to fetch blocked by CORS policy`

**Solution:**
```python
# Di backend-ocr/api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. File Upload Gagal
**Problem**: `File too large` atau `Invalid file type`

**Solutions:**
- Compress gambar (< 10 MB)
- Format yang didukung: JPG, PNG, WEBP, BMP
- Hindari upload PDF/DOC

### General Issues

#### 1. Slow Processing
**Problem**: Validasi memakan waktu > 10 detik

**Solutions:**
- Gunakan preprocessing yang sudah dioptimasi (FastAPI backend)
- Disable GPU jika OCR error (EasyOCR settings)
- Resize image sebelum upload (max 1920px)

#### 2. Duplicate Detection Error
**Problem**: Hash collision atau file `used_hashes.txt` corrupted

**Solution:**
```bash
# Hapus file hash (HATI-HATI: akan reset replay protection)
rm backend-ocr/used_hashes.txt
```

---

## 📊 Monitoring & Analytics

### Audit Log Analysis

```python
import pandas as pd

# Load audit log
df = pd.read_csv('backend-ocr/audit_log.csv')

# Success rate
verified = len(df[df['Status'] == 'VERIFIED'])
total = len(df)
print(f"Auto-approval rate: {verified/total*100:.1f}%")

# Bank distribution
print(df['Bank'].value_counts())

# Average score
print(f"Average score: {df['Score'].mean():.1f}")
```

---

## 🔐 Security Best Practices

1. **API Key Management**
   - Jangan commit `.env` file
   - Gunakan API key yang kuat di production
   - Rotate key secara berkala

2. **Rate Limiting**
   ```python
   # Tambahkan di api.py
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/verify-donation")
   @limiter.limit("10/minute")
   async def verify_donation(...):
       ...
   ```

3. **Input Validation**
   - Sudah ada: file size, file type, amount range
   - Tambahkan: filename sanitization
   - SQL injection protection (jika menggunakan database)

4. **HTTPS Only (Production)**
   ```bash
   # Gunakan reverse proxy (nginx) dengan SSL
   uvicorn api:app --host 127.0.0.1 --port 8000
   ```

---

## 📝 Changelog

### Version 1.0.0 (2026-01-19)
- ✅ Initial release
- ✅ Multi-bank/e-wallet support (13 platforms)
- ✅ Anti-fraud system
- ✅ Replay attack protection
- ✅ Audit logging
- ✅ REST API with FastAPI
- ✅ Next.js frontend

---

## 👥 Kontributor

- **Backend Developer**: OCR & Validation Engine
- **Frontend Developer**: Next.js UI/UX
- **DevOps**: Deployment & Monitoring

---

## 📄 License

MIT License - Copyright (c) 2026 Jalanamal

---

## 🙏 Support

Untuk bug report atau feature request, silakan buat issue di repository ini.

**Jalanamal** - Platform donasi terpercaya untuk berbagai kegiatan sosial dan kemanusiaan.

---

**Made with ❤️ for Jalanamal Community**