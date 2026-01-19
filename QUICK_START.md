# ⚡ Quick Start Guide - Jalanamal OCR Payment Validator

Panduan cepat untuk menjalankan sistem OCR Payment Validator dalam 5 menit!

---

## 📋 Prerequisites

Pastikan sudah terinstall:
- ✅ **Python 3.8+** → [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** → [Download](https://nodejs.org/)
- ✅ **Git** → [Download](https://git-scm.com/)

Cek versi:
```bash
python --version
node --version
npm --version
git --version
```

---

## 🚀 Instalasi Cepat

### 1️⃣ Clone Repository

```bash
git clone <repository-url>
cd OCR_TEST
```

### 2️⃣ Setup Backend (Python)

```bash
# Masuk ke folder backend
cd backend-ocr

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env
# Edit .env jika perlu (opsional untuk testing)
```

**Jika install error:**
```bash
# Install dependencies satu per satu
pip install fastapi uvicorn[standard] python-multipart
pip install easyocr
pip install opencv-python Pillow
pip install python-dotenv
```

### 3️⃣ Setup Frontend (Next.js)

Buka terminal baru:

```bash
# Dari root folder
cd frontend

# Install dependencies
npm install

# Buat file environment (opsional untuk local)
# NEXT_PUBLIC_API_URL akan otomatis ke localhost:8000
```

---

## ▶️ Menjalankan Aplikasi

### Backend (Terminal 1)

```bash
cd backend-ocr
# pastikan venv active
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Tampilan sukses:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ Backend ready di: **http://localhost:8000**

### Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

**Tampilan sukses:**
```
   ▲ Next.js 14.x.x
   - Local:        http://localhost:3000
   - Ready in 2.1s
```

✅ Frontend ready di: **http://localhost:3000**

---

## 🧪 Testing

### 1. Test Backend (Health Check)

Buka browser: http://localhost:8000/health

**Expected response:**
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

### 2. Test API Documentation

Buka browser: http://localhost:8000/docs

Anda akan melihat **Swagger UI** dengan semua endpoint.

### 3. Test Frontend

Buka browser: http://localhost:3000

Anda akan melihat halaman upload screenshot.

### 4. Test Upload Screenshot

**Siapkan screenshot test:**
- Screenshot transfer bank (BCA/Mandiri/dll)
- Yang ada tulisan "BERHASIL"
- Nominal jelas terlihat

**Upload:**
1. Drag & drop screenshot ke halaman
2. Input nominal (misal: 50000)
3. Input bank (misal: BCA)
4. Klik "Verifikasi"

**Expected result:**
- Processing 3-5 detik
- Muncul hasil: VERIFIED/REVIEW/REJECTED
- Ada score dan detail validasi

---

## 📁 Struktur Folder

```
OCR_TEST/
├── backend-ocr/
│   ├── api.py                  # FastAPI app
│   ├── validator.py            # OCR & validation logic
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── audit_log.csv          # Validation logs (auto-generated)
│   ├── used_hashes.txt        # Replay protection (auto-generated)
│   └── venv/                  # Virtual environment
│
├── frontend/
│   ├── app/                   # Next.js pages
│   ├── components/            # React components
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   └── node_modules/          # Installed packages
│
├── README.md                  # Main documentation
├── DEVELOPER_GUIDE.md         # Developer documentation
├── PANDUAN_PENGGUNA.md        # User guide (Indonesian)
└── QUICK_START.md             # This file
```

---

## 🔧 Konfigurasi Dasar

### Backend (.env)

```bash
# backend-ocr/.env
API_SECRET=jalanamal_secure_2026_berkah
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🛠 Troubleshooting Umum

### ❌ Backend tidak start

**Error:** `No module named 'fastapi'`

**Solusi:**
```bash
# Pastikan virtual environment active
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

**Error:** `DLL load failed while importing cv2`

**Solusi:**
```bash
# Install Visual C++ Redistributable (Windows)
# Download dari: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Atau reinstall opencv
pip uninstall opencv-python
pip install opencv-python-headless
```

---

**Error:** `Port 8000 already in use`

**Solusi:**
```bash
# Gunakan port lain
uvicorn api:app --reload --port 8001

# Atau kill process yang pakai port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

---

### ❌ Frontend tidak start

**Error:** `command not found: npm`

**Solusi:**
```bash
# Install Node.js dari https://nodejs.org/
# Restart terminal setelah install
```

---

**Error:** `Module not found: Can't resolve...`

**Solusi:**
```bash
# Delete node_modules dan reinstall
rm -rf node_modules package-lock.json
npm install
```

---

**Error:** `Port 3000 already in use`

**Solusi:**
```bash
# Gunakan port lain
npm run dev -- -p 3001

# Atau kill process
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

---

### ❌ CORS Error saat upload

**Error:** `Access to fetch at 'http://localhost:8000' has been blocked by CORS policy`

**Solusi:**

Pastikan di `backend-ocr/api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart backend setelah edit.

---

### ❌ OCR tidak akurat

**Problem:** Nominal tidak terdeteksi atau salah

**Solusi:**
1. **Screenshot lebih jelas** → hindari blur
2. **Full screen** → jangan crop
3. **Format angka** → pastikan ada "Rp" atau angka jelas
4. **Light mode** → dark mode kadang susah dibaca

**Test preprocessing:**
```bash
cd backend-ocr
python
>>> from validator import preprocess
>>> preprocess("test.jpg")
# Check output file: test_clean.jpg
```

---

## 📊 Monitoring

### Cek Audit Log

```bash
# View audit log
cd backend-ocr
type audit_log.csv     # Windows
# atau
cat audit_log.csv      # Mac/Linux
```

**Format:**
```csv
Time,Bank,Expected,Actual,Score,Status,Notes
2026-01-19 20:00:00,BCA,50000,50000,90,VERIFIED,✅ Platform: BCA | ✅ Amount Perfect Match...
```

### Cek Used Hashes (Replay Protection)

```bash
type used_hashes.txt   # Windows
cat used_hashes.txt    # Mac/Linux
```

Berisi SHA256 hash dari setiap screenshot yang pernah disubmit.

---

## 🔄 Update Code

Jika ada perubahan code:

```bash
# Pull latest changes
git pull

# Update backend dependencies
cd backend-ocr
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd ../frontend
npm install

# Restart both services
```

---

## 🚪 Stopping Services

### Stop Backend
```bash
# Di terminal backend, tekan:
CTRL + C
```

### Stop Frontend
```bash
# Di terminal frontend, tekan:
CTRL + C
```

### Deactivate Virtual Environment (Backend)
```bash
deactivate
```

---

## 📚 Next Steps

Setelah berhasil running:

1. ✅ Baca [README.md](README.md) untuk fitur lengkap
2. ✅ Baca [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) untuk customization
3. ✅ Baca [PANDUAN_PENGGUNA.md](PANDUAN_PENGGUNA.md) untuk user guide
4. ✅ Test dengan berbagai screenshot dari bank berbeda
5. ✅ Customize scoring dan validation logic sesuai kebutuhan
6. ✅ Setup database untuk production (opsional)
7. ✅ Deploy ke server (lihat deployment section di DEVELOPER_GUIDE.md)

---

## 🎯 Production Checklist

Sebelum deploy ke production:

- [ ] Ganti `API_SECRET` dengan value yang aman
- [ ] Set `allow_origins` di CORS ke domain spesifik (bukan `*`)
- [ ] Enable HTTPS
- [ ] Setup rate limiting
- [ ] Setup monitoring (Prometheus/Grafana)
- [ ] Setup database (PostgreSQL/MySQL)
- [ ] Setup backup untuk audit log
- [ ] Test dengan berbagai edge cases
- [ ] Setup error alerting (email/Slack)
- [ ] Performance testing dengan load testing tool

---

## ❓ Butuh Bantuan?

### Documentation:
- 📖 [README.md](README.md) - Overview & fitur lengkap
- 👨‍💻 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Technical docs
- 📱 [PANDUAN_PENGGUNA.md](PANDUAN_PENGGUNA.md) - User guide

### API Docs:
- 🌐 http://localhost:8000/docs - Swagger UI
- 🌐 http://localhost:8000/redoc - ReDoc

### Support:
- 📧 Email: support@jalanamal.com
- 💬 Create issue di repository
- 📞 Contact admin

---

## ✨ Selamat Mencoba!

**Happy validating! 🚀**

Sistem OCR Payment Validator siap digunakan untuk memvalidasi ribuan transaksi dengan cepat dan akurat.

---

**Jalanamal** - Automating charity validation with AI ❤️
