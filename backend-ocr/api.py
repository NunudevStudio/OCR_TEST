from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from validator import extract_data_from_image, validate_donation, log_to_csv
from typing import Optional
import shutil
import os
import glob
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Jalanamal OCR Payment Validator",
    description="API for validating donation/payment screenshots using OCR",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Configuration
API_SECRET = "jalanamal_secure_2026_berkah"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@app.on_event("startup")
async def startup_event():
    """Clean up temporary files on startup"""
    logger.info("Starting Jalanamal OCR API...")
    
    # Clean up old temporary files
    temp_files = glob.glob("temp_*")
    cleaned = 0
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            cleaned += 1
        except Exception as e:
            logger.warning(f"Failed to remove {temp_file}: {e}")
    
    if cleaned > 0:
        logger.info(f"Cleaned up {cleaned} temporary file(s)")
    
    logger.info("API ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Shutting down API...")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    Returns system status and basic diagnostics
    """
    try:
        # Check if critical files exist
        validator_exists = os.path.exists("validator.py")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "dependencies": {
                "validator_module": validator_exists
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.post("/verify-donation")
async def verify_donation(
    x_api_key: str = Header(None),
    file: UploadFile = File(...),
    expected_amount: int = Form(...),
    bank_description: str = Form(...)
):
    """
    Verify donation/payment screenshot using OCR
    
    Args:
        x_api_key: API authentication key
        file: Payment screenshot image
        expected_amount: Expected payment amount
        bank_description: Bank/payment method description
    
    Returns:
        Validation result with status, score, OCR data, and notes
    """
    # Validate API Key
    if not x_api_key or x_api_key != API_SECRET:
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    
    # Validate file is provided
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No file provided"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate expected amount
    if expected_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expected amount must be greater than 0"
        )
    
    temp_path = f"temp_{file.filename}"
    
    try:
        # Read file and check size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        # Save temporary file
        with open(temp_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"Processing file: {file.filename} ({file_size} bytes)")
        
        # Extract data using OCR
        ocr_result = extract_data_from_image(temp_path)
        
        if not ocr_result:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to extract data from image. Image may be corrupted or unreadable."
            )
        
        # Prepare mutation data
        mutation = {
            "amount": expected_amount,
            "description": bank_description
        }
        
        # Validate donation
        score, notes = validate_donation(ocr_result, mutation)
        
        # Determine status
        if score >= 80:
            validation_status = "VERIFIED"
        elif score <= 20:
            validation_status = "REJECTED"
        else:
            validation_status = "REVIEW"
        
        # Log to CSV
        log_to_csv(ocr_result, expected_amount, score, validation_status, notes)
        
        logger.info(f"Validation complete: {validation_status} (score: {score})")
        
        return {
            "status": validation_status,
            "score": score,
            "ocr_data": ocr_result,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"Error processing donation verification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.debug(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {temp_path}: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Jalanamal OCR Payment Validator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "verify_donation": "/verify-donation (POST)"
        }
    }
