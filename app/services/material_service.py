import os
import warnings
from typing import Optional
from fastapi import UploadFile, HTTPException

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    try:
        import pypdf as PyPDF2
    except ImportError:
        import PyPDF2

import pdfplumber
from docx import Document

from app.core.config import settings


class MaterialService:
    """Service for handling study material uploads and text extraction."""
    
    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """Validate uploaded file type and size."""
        # Check file type
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_extension}' not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        return True
    
    @staticmethod
    async def save_file(file: UploadFile, user_id: int) -> str:
        """Save uploaded file to disk."""
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        unique_filename = f"{user_id}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return file_path
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        
        try:
            # Try pdfplumber first (better text extraction)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to extract text from PDF: {str(e2)}"
                )
        
        return text.strip()
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                text += "\n"
            
            return text.strip()
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from DOCX: {str(e)}"
            )
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to read text file: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read text file: {str(e)}"
            )
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """Extract text from file based on type."""
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return MaterialService.extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            return MaterialService.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return MaterialService.extract_text_from_txt(file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_type}"
            )
    
    @staticmethod
    def clean_extracted_text(text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        # Keep basic punctuation and alphanumeric characters
        import re
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        return text.strip()
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path)
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from disk."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
