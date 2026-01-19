import easyocr
import re
import cv2
import numpy as np
import csv
import os
import logging
import hashlib
from datetime import datetime
from PIL import Image, ExifTags
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

# OCR Reader - Lazy loaded singleton
_reader_instance: Optional[easyocr.Reader] = None

def get_ocr_reader() -> easyocr.Reader:
    """Get or create OCR reader instance (singleton pattern)"""
    global _reader_instance
    if _reader_instance is None:
        logger.info("Initializing EasyOCR reader...")
        _reader_instance = easyocr.Reader(['id', 'en'], gpu=False)
        logger.info("EasyOCR reader initialized")
    return _reader_instance

# =====================================================
# BEHAVIOR DATABASE (DNA STRUK ASLI) - FLEXIBLE VERSION
# =====================================================
# Updated: Lebih fleksibel untuk handle variasi UI setiap bank
# Fokus: Brand detection + Success indicator (bukan keyword spesifik)
BANK_BEHAVIORS = {
    "BCA": {
        # Cukup ada brand BCA + indikasi berhasil
        "brand_keywords": ["BCA", "BANK CENTRAL ASIA"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS", "SELESAI", "COMPLETED"],
        "forbidden": ["INVOICE", "ORDER ID", "BELANJA", "MARKETPLACE"],
        "amount_keywords": ["RP", "JUMLAH", "NOMINAL", "TOTAL"],
        "id_pattern": r"(BUKTI|REF|REFERENSI|NO\s*TRANSAKSI|TRANSACTION\s*ID)[:\s]*([A-Z0-9]+)"
    },
    "BRI": {
        "brand_keywords": ["BRI", "BANK RAKYAT INDONESIA"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS", "SELESAI"],
        "forbidden": ["INVOICE", "QRIS"],
        "amount_keywords": ["RP", "JUMLAH", "NOMINAL"],
        "id_pattern": r"(NOMOR|NO\.*)\s*(REFERENSI|REF)[:\s]*(\d+)"
    },
    "MANDIRI": {
        "brand_keywords": ["MANDIRI", "BANK MANDIRI", "LIVIN"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS"],
        "forbidden": ["ORDER ID", "BELANJA"],
        "amount_keywords": ["RP", "JUMLAH", "NOMINAL"],
        "id_pattern": r"(NO\.*\s*TRANSAKSI|TRANSACTION\s*ID)[:\s]*([A-Z0-9]+)"
    },
    "BSI": {
        "brand_keywords": ["BSI", "BANK SYARIAH INDONESIA", "BANK SYARIAH"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS"],
        "forbidden": ["ORDER", "BELANJA"],
        "amount_keywords": ["RP", "JUMLAH", "NOMINAL"],
        "id_pattern": r"(NOMOR|NO\.*)\s*(TRANSAKSI)[:\s]*([A-Z0-9]+)"
    },
    "BNI": {
        "brand_keywords": ["BNI", "BANK NEGARA INDONESIA"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS", "SELESAI"],
        "forbidden": ["INVOICE", "ORDER"],
        "amount_keywords": ["RP", "JUMLAH"],
        "id_pattern": r"(REFERENSI|REF)[:\s]*([A-Z0-9]+)"
    },
    "CIMB": {
        "brand_keywords": ["CIMB", "CIMB NIAGA"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS"],
        "forbidden": ["INVOICE"],
        "amount_keywords": ["RP", "AMOUNT"],
        "id_pattern": r"(TRANSACTION\s*ID|REF)[:\s]*([A-Z0-9]+)"
    },
    "PERMATA": {
        "brand_keywords": ["PERMATA", "PERMATABANK"],
        "success_indicators": ["BERHASIL", "SUKSES"],
        "forbidden": ["INVOICE"],
        "amount_keywords": ["RP", "JUMLAH"],
        "id_pattern": r"(REF|REFERENSI)[:\s]*([A-Z0-9]+)"
    },
    "BTN": {
        "brand_keywords": ["BTN", "BANK TABUNGAN NEGARA"],
        "success_indicators": ["BERHASIL", "SUCCESS"],
        "forbidden": ["INVOICE"],
        "amount_keywords": ["RP"],
        "id_pattern": r"(NO\.*\s*REF)[:\s]*([A-Z0-9]+)"
    },
    "DANA": {
        "brand_keywords": ["DANA"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS"],
        "forbidden": ["M-TRANSFER"],  # DANA bukan bank transfer
        "amount_keywords": ["RP", "TOTAL", "BAYAR"],
        "id_pattern": r"(ID\s*DANA|TRANSACTION\s*ID)[:\s]*(\d+)"
    },
    "GOPAY": {
        "brand_keywords": ["GOPAY", "GOJEK"],
        "success_indicators": ["BERHASIL", "SELESAI", "SUCCESS", "COMPLETED"],
        "forbidden": ["M-TRANSFER"],
        "amount_keywords": ["RP", "TOTAL"],
        "id_pattern": r"(ORDER\s*ID|ID\s*TRANSAKSI)[:\s]*([A-Z0-9-]+)"
    },
    "OVO": {
        "brand_keywords": ["OVO"],
        "success_indicators": ["BERHASIL", "SUKSES", "SUCCESS"],
        "forbidden": ["M-TRANSFER"],
        "amount_keywords": ["RP", "TOTAL"],
        "id_pattern": r"(ID\s*TRANSAKSI|TRANSACTION\s*ID)[:\s]*([A-Z0-9.]+)"
    },
    "SHOPEEPAY": {
        "brand_keywords": ["SHOPEEPAY", "SHOPEE PAY"],
        "success_indicators": ["BERHASIL", "SUCCESS"],
        "forbidden": ["M-TRANSFER"],
        "amount_keywords": ["RP", "TOTAL"],
        "id_pattern": r"(ORDER\s*ID|REF)[:\s]*([A-Z0-9]+)"
    },
    "LINKAJA": {
        "brand_keywords": ["LINKAJA", "LINK AJA"],
        "success_indicators": ["BERHASIL", "SUKSES"],
        "forbidden": ["M-TRANSFER"],
        "amount_keywords": ["RP", "TOTAL"],
        "id_pattern": r"(ID\s*TRANSAKSI)[:\s]*([A-Z0-9]+)"
    }
}

# =====================================================
# IMAGE FORENSIC
# =====================================================
def check_metadata(path: str) -> Tuple[bool, Optional[str]]:
    """Check if image has been edited using common editing tools
    
    Args:
        path: Path to image file
    
    Returns:
        Tuple of (is_edited, software_name)
    """
    tools = ["ADOBE", "PHOTOSHOP", "CANVA", "GIMP", "PICSART"]
    try:
        img = Image.open(path)
        exif = img._getexif()
        if not exif:
            return False, None
        for tag, val in exif.items():
            name = ExifTags.TAGS.get(tag, tag)
            if name == "Software":
                for t in tools:
                    if t in str(val).upper():
                        return True, str(val)
        return False, None
    except Exception as e:
        logger.warning(f"Failed to check metadata for {path}: {e}")
        return False, None

def preprocess(path: str) -> str:
    """Preprocess image for better OCR accuracy - OPTIMIZED VERSION
    
    Uses fast preprocessing suitable for mobile app screenshots.
    Avoids slow operations like fastNlMeansDenoising.
    
    Args:
        path: Path to input image
    
    Returns:
        Path to preprocessed image
    """
    try:
        img = cv2.imread(path)
        if img is None:
            logger.warning(f"Failed to load image: {path}")
            return path

        # Upscale small images for better OCR
        if img.shape[1] < 900:
            img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # OPTIMIZED: Fast preprocessing for mobile screenshots
        # Use GaussianBlur instead of slow fastNlMeansDenoising
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # CLAHE for contrast enhancement (handles watermarks well)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        # Save preprocessed image
        out = path.replace(".", "_clean.")
        cv2.imwrite(out, enhanced)
        
        logger.info("Preprocessed with fast CLAHE+blur strategy")
        return out
    
    except Exception as e:
        logger.error(f"Error preprocessing image {path}: {e}")
        return path

# =====================================================
# OCR & EXTRACTION
# =====================================================
def detect_bank(text: str) -> str:
    """Detect bank from OCR text based on brand keywords (flexible)
    
    Args:
        text: OCR extracted text
    
    Returns:
        Detected bank name or "UNKNOWN"
    """
    t = text.upper()
    scores = {}
    
    for bank, behavior in BANK_BEHAVIORS.items():
        score = 0
        
        # Check brand keywords (strong indicator)
        for brand in behavior["brand_keywords"]:
            if brand in t:
                score += 10
        
        # Check success indicators (confirmation it's a successful transaction)
        for indicator in behavior["success_indicators"]:
            if indicator in t:
                score += 5
                break  # One success indicator is enough
        
        # Check amount keywords (should have Rp/nominal somewhere)
        for amt_keyword in behavior["amount_keywords"]:
            if amt_keyword in t:
                score += 2
                break
        
        # Penalty for forbidden words
        for forbidden in behavior["forbidden"]:
            if forbidden in t:
                score -= 20  # Heavy penalty
        
        scores[bank] = score
    
    # Get best match
    if not scores:
        return "UNKNOWN"
    
    best_bank = max(scores, key=scores.get)
    best_score = scores[best_bank]
    
    # Require minimum score of 10 (at least one brand keyword)
    if best_score >= 10:
        logger.info(f"Bank detected: {best_bank} (score: {best_score})")
        return best_bank
    
    logger.warning(f"No bank detected with sufficient confidence. Best: {best_bank}={best_score}")
    return "UNKNOWN"

def clean_currency(text: str) -> int:
    """Extract numeric value from currency string - handles Indonesian format
    
    Indonesian format: 10.546,00 (dot = thousand separator, comma = decimal)
    International: 10,546.00 (comma = thousand, dot = decimal)
    
    Args:
        text: Currency string (e.g., "Rp 10.546,00" or "10.546" or "10546")
    
    Returns:
        Integer value or 0 if parsing fails
    """
    # Remove all non-numeric except dots and commas
    # Handle both Indonesian (10.546,00) and international (10,546.00) formats
    
    # Replace thousand separators (both . and ,) with nothing
    # Keep only last separator if it's a decimal separator
    cleaned = text.strip()
    
    # Remove "Rp" or "IDR" prefix
    cleaned = re.sub(r'(?i)(rp|idr)\s*', '', cleaned)
    
    # Check if has decimal separator (last dot or comma)
    # Indonesian: 10.546,00 -> remove dots, convert comma to dot -> 10546.00
    # International: 10,546.00 -> remove commas -> 10546.00
    
    if ',' in cleaned and '.' in cleaned:
        # Has both - determine which is decimal
        last_comma_pos = cleaned.rfind(',')
        last_dot_pos = cleaned.rfind('.')
        
        if last_comma_pos > last_dot_pos:
            # Indonesian format: 10.546,00
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # International format: 10,546.00
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Only comma - could be thousand separator or decimal
        # If only one comma and 2 digits after it, it's decimal
        if cleaned.count(',') == 1 and len(cleaned.split(',')[1]) == 2:
            # Decimal separator: 10546,00
            cleaned = cleaned.replace(',', '.')
        else:
            # Thousand separator: 10,546
            cleaned = cleaned.replace(',', '')
    elif '.' in cleaned:
        # Only dot - could be thousand separator or decimal
        # If multiple dots or last section has 3+ digits, it's thousand separator
        if cleaned.count('.') > 1 or len(cleaned.split('.')[-1]) > 2:
            # Thousand separator: 10.546.789
            cleaned = cleaned.replace('.', '')
        # else: decimal separator (keep it)
    
    # Now extract just the numeric part
    match = re.search(r'\d+\.?\d*', cleaned)
    if match:
        num_str = match.group()
        try:
            # Convert to float first, then to int (removes decimal part)
            return int(float(num_str))
        except ValueError:
            return 0
    
    return 0

def extract_data_from_image(path: str) -> Optional[Dict[str, Any]]:
    """Extract payment data from screenshot using OCR
    
    Args:
        path: Path to payment screenshot
    
    Returns:
        Dictionary containing extracted data or None if processing fails
    """
    try:
        if not os.path.exists(path):
            logger.error(f"Image file not found: {path}")
            return None
        
        # Check for editing software traces
        edited, software = check_metadata(path)
        
        # Preprocess image
        clean = preprocess(path)
        
        # Get OCR reader and process
        reader = get_ocr_reader()
        ocr_raw = reader.readtext(clean, detail=1, paragraph=False)
        
        if not ocr_raw:
            logger.warning(f"No text detected in image: {path}")
            return None
        
        text = " ".join([r[1] for r in ocr_raw])

        # Calculate OCR confidence
        low_conf = sum(1 for r in ocr_raw if r[2] < 0.6)
        noise_ratio = low_conf / len(ocr_raw) if ocr_raw else 1

        # Detect bank
        bank = detect_bank(text)

        # Extract amounts - try multiple patterns for robustness
        amounts = []
        
        # Pattern 1: "Rp 10.546" or "Rp10.546" (standard Indonesian)
        amounts.extend(re.findall(r'(?:RP|Rp|rp)\s*[\d\.,]+', text))
        
        # Pattern 2: "10.546,00" or "10546" (number then maybe Rp after)
        amounts.extend(re.findall(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?', text))
        
        # Pattern 3: Just numbers with dots/commas (fallback)
        amounts.extend(re.findall(r'\d+[.,]\d+', text))
        
        # Clean and filter amounts
        values = []
        for amt_text in amounts:
            cleaned = clean_currency(amt_text)
            # Filter reasonable donation amounts (> 1000, < 1 billion)
            if 1000 < cleaned < 1_000_000_000:
                values.append(cleaned)
        
        # Remove duplicates and get the most likely amount
        # Usually the largest amount is the transaction total
        values = sorted(set(values), reverse=True)

        # Extract transaction ID
        tx_id = "-"
        if bank in BANK_BEHAVIORS:
            m = re.search(BANK_BEHAVIORS[bank]["id_pattern"], text, re.IGNORECASE)
            if m:
                tx_id = m.group(len(m.groups()))

        return {
            "raw_text": text,
            "nominal": max(values) if values else 0,
            "bank_detected": bank,
            "transaction_id": tx_id,
            "ocr_noise": noise_ratio,
            "is_suspicious": edited,
            "software_trace": software,
            "hash": hashlib.sha256(text.encode()).hexdigest()
        }
    
    except Exception as e:
        logger.error(f"Error extracting data from image {path}: {e}", exc_info=True)
        return None

# =====================================================
# VALIDATION CORE (ANTI CHEAT)
# =====================================================
def validate_donation(ocr: Optional[Dict[str, Any]], mutation: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Validate donation screenshot against expected data - FLEXIBLE VERSION
    
    Uses flexible validation suitable for different bank UI versions.
    Focus on essential checks: amount, success status, legitimacy.
    
    Args:
        ocr: OCR extracted data dictionary
        mutation: Expected transaction data
    
    Returns:
        Tuple of (score, validation_notes)
        Score: 0-100, where >=80 is verified, <=20 is rejected
    """
    reasons: List[str] = []
    score = 0

    if not ocr:
        return 0, ["OCR FAILED"]

    # Check 1: Anti-fraud - Edited image detection
    if ocr["is_suspicious"]:
        return 0, [f"⛔ FILE EDITED ({ocr['software_trace']})"]

    # Check 2: Anti-fraud - Template detection
    if ocr["ocr_noise"] < 0.05:
        return 0, ["⛔ OCR TOO CLEAN (TEMPLATE SUSPECTED)"]

    # Check 3: Bank/Platform Detection (relaxed - just needs brand)
    bank = ocr["bank_detected"]
    if bank == "UNKNOWN":
        # Tidak langsung reject - bisa saja bank baru atau UI aneh
        # Tapi kurangi score significantly
        score -= 30
        reasons.append("⚠️ BANK/PLATFORM NOT CLEARLY IDENTIFIED")
    else:
        score += 20
        reasons.append(f"✅ Platform: {bank}")

    text = ocr["raw_text"].upper()
    
    # Check 4: Success Indicator (PENTING - harus ada indikasi "berhasil")
    if bank in BANK_BEHAVIORS:
        behavior = BANK_BEHAVIORS[bank]
        has_success = any(indicator in text for indicator in behavior["success_indicators"])
        
        if has_success:
            score += 20
            reasons.append("✅ Transaction Success Confirmed")
        else:
            score -= 20
            reasons.append("⚠️ No success confirmation found")
        
        # Check forbidden words (invoice, shopping, etc)
        has_forbidden = any(f in text for f in behavior["forbidden"])
        if has_forbidden:
            return 0, ["❌ FORBIDDEN CONTENT (Not a bank transfer - shopping/invoice detected)"]
    else:
        # Unknown bank - check generic success indicators
        generic_success = any(word in text for word in ["BERHASIL", "SUKSES", "SUCCESS", "SELESAI"])
        if generic_success:
            score += 10
            reasons.append("✅ Generic success indicator found")

    # Check 5: Amount Validation (CRITICAL - ini yang paling penting)
    expected = mutation["amount"]
    actual = ocr["nominal"]

    if actual == 0:
        return 0, ["❌ NOMINAL NOT FOUND IN SCREENSHOT"]

    diff = abs(actual - expected)
    if diff == 0:
        score += 30  # Perfect match
        reasons.append(f"✅ Amount Perfect Match: Rp {actual:,}")
    elif diff <= 999:
        score += 20  # Close enough (kode unik tolerance)
        reasons.append(f"✅ Amount Match (±{diff}): Rp {actual:,}")
    else:
        # Mismatch - tapi jangan langsung reject, bisa typo di input
        score -= 40
        reasons.append(f"⚠️ AMOUNT MISMATCH - Expected: Rp {expected:,}, Detected: Rp {actual:,}")

    # Check 6: Replay Protection - Prevent duplicate submission
    try:
        if os.path.exists("used_hashes.txt"):
            with open("used_hashes.txt", "r", encoding="utf-8") as f:
                used_hashes = f.read()
                if ocr["hash"] in used_hashes:
                    return 0, ["❌ DUPLICATE RECEIPT (Already submitted before)"]

        # Save hash
        with open("used_hashes.txt", "a", encoding="utf-8") as f:
            f.write(ocr["hash"] + "\n")
        
        score += 10
        reasons.append("✅ Unique submission")
        
    except Exception as e:
        logger.error(f"Error checking/updating hash file: {e}")

    # Check 7: Transaction ID (bonus - not critical)
    if ocr["transaction_id"] != "-":
        score += 10
        reasons.append(f"✅ TX ID: {ocr['transaction_id']}")

    # Final scoring and status
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    logger.info(f"Validation score: {score}/100 for {bank}")
    
    return score, reasons

# =====================================================
# LOGGING
# =====================================================
def log_to_csv(ocr: Dict[str, Any], expected: int, score: int, status: str, notes: List[str]) -> None:
    """Log validation result to CSV audit file
    
    Args:
        ocr: OCR extracted data
        expected: Expected amount
        score: Validation score
        status: Validation status (VERIFIED/REVIEW/REJECTED)
        notes: Validation notes
    """
    file = "audit_log.csv"
    exists = os.path.isfile(file)

    try:
        with open(file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["Time", "Bank", "Expected", "Actual", "Score", "Status", "Notes"])
            w.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ocr["bank_detected"],
                expected,
                ocr["nominal"],
                score,
                status,
                " | ".join(notes)
            ])
        logger.info(f"Logged validation result to {file}")
    except Exception as e:
        logger.error(f"Failed to log to CSV: {e}")
