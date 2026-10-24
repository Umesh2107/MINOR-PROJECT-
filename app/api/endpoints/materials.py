from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.models.material import StudyMaterial
from app.schemas.material import Material, MaterialUploadResponse
from app.api.deps import get_current_user, get_current_professor
from app.services.material_service import MaterialService

router = APIRouter()


@router.post("/upload", response_model=MaterialUploadResponse)
async def upload_material(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Upload study material (PDF, DOCX, TXT) and extract text."""
    try:
        # Validate file
        MaterialService.validate_file(file)
        
        # Save file to disk
        file_path = await MaterialService.save_file(file, current_user.id)
        
        # Determine file type
        file_ext = file.filename.split('.')[-1].lower()
        file_size = MaterialService.get_file_size(file_path)
        
        # Extract text
        extracted_text = ""
        try:
            raw_text = MaterialService.extract_text(file_path, file_ext)
            extracted_text = MaterialService.clean_extracted_text(raw_text)
        except Exception as ex:
            extracted_text = f"Text extraction warning: {str(ex)}"
        
        # Save to database
        material_title = title if title else file.filename
        study_material = StudyMaterial(
            user_id=current_user.id,
            title=material_title,
            file_path=file_path,
            file_type=file_ext,
            file_size=file_size,
            extracted_text=extracted_text
        )
        
        db.add(study_material)
        db.commit()
        db.refresh(study_material)
        
        return MaterialUploadResponse(
            id=study_material.id,
            title=study_material.title,
            file_type=study_material.file_type,
            file_size=study_material.file_size,
            extracted_text=study_material.extracted_text,
            message="Material uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{material_id}", response_model=Material)
def get_material(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get material details."""
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    return material


@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Delete a material."""
    material = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    
    # Remove file from disk
    MaterialService.delete_file(material.file_path)
    
    # Delete from DB
    db.delete(material)
    db.commit()
    
    return {"message": "Material deleted successfully"}


@router.post("/{material_id}/extract")
async def extract_text(
    material_id: int,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Extract text from uploaded material."""
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    
    raw_text = MaterialService.extract_text(material.file_path, material.file_type)
    cleaned_text = MaterialService.clean_extracted_text(raw_text)
    
    material.extracted_text = cleaned_text
    db.commit()
    
    return {
        "material_id": material.id,
        "extracted_text": cleaned_text
    }
