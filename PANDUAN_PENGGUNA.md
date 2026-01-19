# 📖 Panduan Pengguna - Jalanamal OCR Payment Validator

Panduan lengkap untuk pengguna dalam menggunakan sistem validasi pembayaran otomatis.

---

## 🎯 Apa itu OCR Payment Validator?

**OCR Payment Validator** adalah sistem otomatis yang dapat memverifikasi keaslian screenshot pembayaran/donasi menggunakan teknologi kecerdasan buatan (AI).

### Manfaat:
- ✅ **Hemat Waktu**: Validasi otomatis dalam hitungan detik
- ✅ **Akurat**: Deteksi nominal, bank, dan status transaksi secara otomatis
- ✅ **Anti-Penipuan**: Mendeteksi screenshot yang diedit atau palsu
- ✅ **Audit Trail**: Semua validasi tercatat untuk tracking

---

## 🚀 Cara Menggunakan

### Langkah 1: Buka Aplikasi

Akses aplikasi melalui browser:
```
http://localhost:3000
```
(atau URL yang diberikan oleh admin)

### Langkah 2: Siapkan Screenshot Pembayaran

**Screenshot yang Valid:**
- ✅ Screenshot **langsung** dari aplikasi banking
- ✅ **Full screen** (bukan cropped)
- ✅ **Jelas** (tidak blur)
- ✅ Ada tulisan "**BERHASIL**" atau "**SUKSES**"
- ✅ Terlihat **nominal** pembayaran
- ✅ Terlihat **nama bank/e-wallet**

**Screenshot yang TIDAK Valid:**
- ❌ Screenshot yang sudah diedit (Photoshop, Canva, dll)
- ❌ Screenshot invoice belanja online
- ❌ Screenshot pending/gagal
- ❌ Foto kamera (bukan screenshot)
- ❌ Screenshot blur atau terpotong

### Langkah 3: Upload Screenshot

1. Klik tombol **"Upload Screenshot"** atau drag & drop file
2. Pilih file screenshot dari perangkat Anda
3. Format yang didukung: JPG, PNG, WEBP
4. Maksimal ukuran file: 10 MB

### Langkah 4: Isi Informasi

**Field yang perlu diisi:**

#### **Nominal yang Diharapkan**
- Masukkan jumlah pembayaran yang seharusnya
- Contoh: `50000` (untuk Rp 50.000)
- Jangan gunakan titik atau koma

#### **Deskripsi Bank** (opsional)
- Nama bank atau e-wallet
- Contoh: `BCA`, `DANA`, `GoPay`
- Digunakan untuk konfirmasi tambahan

### Langkah 5: Klik "Verifikasi"

Sistem akan memproses screenshot Anda dalam 3-5 detik.

### Langkah 6: Lihat Hasil

Sistem akan memberikan hasil dengan 3 kemungkinan status:

---

## ✅ Status VERIFIED (Terverifikasi)

**Artinya:**
Screenshot Anda **valid** dan **sesuai** dengan data yang diharapkan.

**Tindakan:**
- Pembayaran dapat langsung di-approve
- Tidak perlu review manual

**Contoh:**
```
Status: VERIFIED ✅
Score: 90/100

Detail:
✅ Platform: BCA
✅ Transaction Success Confirmed
✅ Amount Perfect Match: Rp 50,000
✅ Unique submission
✅ TX ID: TRX123456789
```

---

## ⚠️ Status REVIEW (Perlu Review)

**Artinya:**
Screenshot Anda **mungkin valid**, tetapi ada hal yang perlu dicek manual oleh admin.

**Alasan umum:**
- Nominal tidak sama persis (ada kode unik)
- Bank tidak terdeteksi jelas
- OCR tidak menangkap semua informasi

**Tindakan:**
- Tunggu admin untuk review manual
- Admin akan cek screenshot secara manual
- Proses bisa memakan waktu lebih lama

**Contoh:**
```
Status: REVIEW ⚠️
Score: 65/100

Detail:
✅ Platform: BCA
✅ Transaction Success Confirmed
⚠️ AMOUNT MISMATCH - Expected: Rp 50,000, Detected: Rp 50,123
✅ Unique submission
```

**Tips jika sering REVIEW:**
- Pastikan screenshot full screen
- Jangan crop gambar
- Pastikan nominal input sesuai (termasuk kode unik jika ada)

---

## ❌ Status REJECTED (Ditolak)

**Artinya:**
Screenshot Anda **tidak valid** atau **terdeteksi mencurigakan**.

**Alasan umum:**
1. **File sudah diedit**
   ```
   ⛔ FILE EDITED (Adobe Photoshop)
   ```
   - Screenshot telah dimodifikasi menggunakan software editing
   - **Solusi**: Kirim screenshot asli dari HP

2. **Bukan transfer bank**
   ```
   ❌ FORBIDDEN CONTENT (Not a bank transfer - invoice detected)
   ```
   - Screenshot adalah invoice belanja online
   - **Solusi**: Kirim screenshot transfer bank yang benar

3. **Screenshot duplicate**
   ```
   ❌ DUPLICATE RECEIPT (Already submitted before)
   ```
   - Screenshot ini sudah pernah disubmit sebelumnya
   - **Solusi**: Pastikan ini transaksi baru

4. **Nominal tidak ditemukan**
   ```
   ❌ NOMINAL NOT FOUND IN SCREENSHOT
   ```
   - OCR tidak bisa membaca nominal di screenshot
   - **Solusi**: Pastikan screenshot jelas dan tidak blur

5. **Template/Palsu**
   ```
   ⛔ OCR TOO CLEAN (TEMPLATE SUSPECTED)
   ```
   - Screenshot terlalu "bersih" dan terindikasi template
   - **Solusi**: Screenshot langsung dari aplikasi banking asli

**Tindakan:**
- Cek alasan penolakan
- Perbaiki masalah
- Upload ulang screenshot yang benar
- Jika yakin screenshot valid, hubungi admin

---

## 🏦 Bank & E-Wallet yang Didukung

### Perbankan:
- ✅ **BCA** (Bank Central Asia)
- ✅ **BRI** (Bank Rakyat Indonesia)
- ✅ **Mandiri** / Livin'
- ✅ **BSI** (Bank Syariah Indonesia)
- ✅ **BNI** (Bank Negara Indonesia)
- ✅ **CIMB Niaga**
- ✅ **Permata Bank**
- ✅ **BTN** (Bank Tabungan Negara)

### E-Wallet:
- ✅ **DANA**
- ✅ **GoPay**
- ✅ **OVO**
- ✅ **ShopeePay**
- ✅ **LinkAja**

**Catatan:** Bank/e-wallet lain mungkin juga bisa terdeteksi, tapi belum dioptimalkan.

---

## 💡 Tips & Trik

### 1. Cara Screenshot yang Benar

**Android:**
- Tekan tombol **Power + Volume Down** bersamaan
- Atau gunakan fitur screenshot di quick settings

**iPhone:**
- **iPhone X ke atas**: Tekan **Side Button + Volume Up**
- **iPhone 8 ke bawah**: Tekan **Home Button + Power**

### 2. Pastikan Screenshot Lengkap

Screenshot harus menampilkan minimal:
- ✅ Logo bank/e-wallet
- ✅ Tulisan "Berhasil" atau "Sukses"
- ✅ Nominal transfer (Rp XXX)
- ✅ Waktu transaksi
- ✅ Nomor referensi/transaksi (jika ada)

### 3. Jangan Edit Screenshot

- ❌ Jangan crop/potong
- ❌ Jangan tambah text/sticker
- ❌ Jangan filter/color adjustment
- ❌ Jangan compress berlebihan

### 4. Input Nominal yang Tepat

**Jika ada kode unik:**
```
Transfer: Rp 50.123 (50.000 + 123 kode unik)
Input di form: 50123 (dengan kode unik)
```

**Jika tanpa kode unik:**
```
Transfer: Rp 50.000
Input di form: 50000
```

### 5. Koneksi Internet Stabil

- Proses OCR membutuhkan internet
- Pastikan koneksi stabil saat upload
- Jika gagal, coba refresh dan upload ulang

---

## ❓ FAQ (Pertanyaan Sering Diajukan)

### Q: Berapa lama proses validasi?
**A:** Sekitar 3-5 detik untuk OCR dan validasi otomatis.

### Q: Apakah data saya aman?
**A:** Ya, screenshot hanya diproses dan tidak disimpan permanen. Hanya hash (sidik jari) yang disimpan untuk mencegah duplikasi.

### Q: Screenshot saya valid tapi ditolak, kenapa?
**A:** Kemungkinan:
1. Screenshot blur/tidak jelas → upload ulang yang lebih jelas
2. Bank belum didukung → hubungi admin
3. Format angka tidak terbaca → coba screenshot ulang

### Q: Bisa pakai foto kamera?
**A:** **Tidak disarankan**. Gunakan screenshot langsung dari HP untuk hasil terbaik.

### Q: Screenshot saya sudah diedit untuk menutupi data pribadi, apakah masalah?
**A:** **Ya, akan ditolak**. Sistem mendeteksi editing. Jika perlu sensor data pribadi, hubungi admin untuk cara yang aman.

### Q: Berapa kali saya bisa upload?
**A:** Ada limit 10 kali per menit untuk mencegah spam.

### Q: Screenshot dari galeri HP bisa?
**A:** **Bisa**, selama:
- Screenshot asli (belum diedit)
- Masih jelas (tidak terlalu lama/compress)

### Q: Nominal saya Rp 50.000 tapi terdeteksi Rp 50.123, kenapa?
**A:** OCR mendeteksi ada angka tambahan. Cek screenshot Anda, mungkin ada:
- Kode unik (123)
- Biaya admin yang tertera
- Angka lain di screenshot

**Solusi:** Input nominal yang sesuai dengan yang terdeteksi.

### Q: Bank saya tidak terdeteksi, apakah gagal?
**A:** Tidak selalu gagal. Hasil akan masuk status **REVIEW** dan akan dicek manual oleh admin.

---

## 🆘 Troubleshooting

### Problem: Upload gagal terus

**Solusi:**
1. Cek ukuran file (maksimal 10 MB)
2. Cek format file (harus JPG/PNG/WEBP)
3. Cek koneksi internet
4. Refresh halaman dan coba lagi
5. Coba browser lain (Chrome/Firefox)

### Problem: Loading terlalu lama

**Solusi:**
1. Tunggu hingga 10 detik
2. Jika masih loading, refresh halaman
3. Coba compress gambar (tapi jangan terlalu kecil)
4. Cek koneksi internet

### Problem: Hasil tidak akurat

**Solusi:**
1. Upload screenshot yang lebih jelas
2. Screenshot full screen (jangan crop)
3. Pastikan screenshot dari aplikasi banking asli
4. Hindari screenshot dark mode jika hasilnya tidak bagus

### Problem: Selalu REVIEW terus

**Solusi:**
1. Pastikan nominal input **tepat** sama dengan di screenshot
2. Pastikan ada tulisan "BERHASIL" di screenshot
3. Screenshot dari aplikasi banking resmi (bukan browser)

---

## 📞 Hubungi Admin

Jika masih ada masalah atau pertanyaan:

- 📧 Email: support@jalanamal.com
- 💬 WhatsApp: 0812-XXXX-XXXX
- 🌐 Website: jalanamal.com

---

## 📝 Checklist Sebelum Upload

Sebelum mengupload screenshot, pastikan:

- [ ] Screenshot **langsung** dari aplikasi banking (bukan edit)
- [ ] Screenshot **full screen** dan **jelas**
- [ ] Ada tulisan "**Berhasil**" atau "**Sukses**"
- [ ] **Nominal** terlihat jelas
- [ ] **Nama bank** terlihat
- [ ] Ukuran file **< 10 MB**
- [ ] Format file **JPG/PNG/WEBP**
- [ ] Input nominal **sesuai** (termasuk kode unik jika ada)

---

## 🎉 Selamat!

Anda sudah siap menggunakan **Jalanamal OCR Payment Validator**.

**Terima kasih** telah berkontribusi untuk Jalanamal! 🙏

---

**Jalanamal** - Platform donasi terpercaya untuk kemanusiaan.

*Diberkahi dalam setiap langkah* ✨
