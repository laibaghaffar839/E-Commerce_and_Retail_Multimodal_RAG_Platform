from fastapi import APIRouter, UploadFile, File, Depends, HTTPException,status
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from db.database import get_db
from db.models import UploadedFile, User, ChatRoom
from services.auth import get_current_user

from services.ingestion.pdf import extract_pdf
from services.ingestion.docx import extract_docx
from services.ingestion.csv import extract_csv
from services.ingestion.txt import extract_txt
from services.ingestion.markdown import extract_md
from services.ingestion.pptx import extract_pptx
from services.ingestion.audio import extract_audio
from services.ingestion.video import extract_video
from services.ingestion.image import extract_image

from services.chunker import chunk_text
from services.embedder import embed_text
from services.qdrant import store_chunks

router = APIRouter(prefix="/upload",tags=["Upload"])

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# get files route
@router.get("/{room_id}")
def get_uploaded_files(room_id: int,current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)):

    # Check room belongs to logged-in user
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
    ).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )


    # Get all uploaded files for this room
    uploaded_files = db.query(UploadedFile).filter(
        UploadedFile.room_id == room_id
    ).order_by(
        UploadedFile.uploaded_at.desc()
    ).all()


    return uploaded_files

# Post route
@router.post("/{room_id}")
def upload_file(room_id: int,file: UploadFile = File(...),current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):

    # Check room belongs to logged-in user
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
        ).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )


    # 1. Check file extension
    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    extension = filename.split(".")[-1].lower()


    # 2. Supported file types
    supported_types = ["pdf", "docx", "csv","txt","md","jpg","jpeg","png",
                       "pptx","mp3","wav","m4a","mp4","mov","avi"]

    if extension not in supported_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )


    # 3. Save file
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(UPLOAD_DIR,unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    # 4. Create UploadedFile database record
    uploaded_file = UploadedFile(
        room_id=room_id,
        filename=filename,
        file_type=extension,
        file_path=file_path,
        status="processing"
    )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)


    try:

        # 5. Select extractor basically this is the replacement of if-else
        EXTRACTORS = {
        "pdf": extract_pdf,
        "docx": extract_docx,
        "csv": extract_csv,
        "txt": extract_txt,
        "md": extract_md,
        "pptx": extract_pptx,
        "mp3": extract_audio,
        "wav": extract_audio,
        "m4a": extract_audio,
        "mp4": extract_video,
        "mov": extract_video,
        "avi": extract_video,
        "jpg": extract_image,
        "jpeg": extract_image,
        "png": extract_image,
        }

        extractor = EXTRACTORS.get(extension)

        if extractor is None:
            raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
            )
        
        extracted_text = extractor(file_path)

        # Make sure something was extracted
        if not extracted_text:
            raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the uploaded file."
            )
        # 6. Create chunks
        chunks = chunk_text(extracted_text)

        embeddings = [embed_text(chunk) for chunk in chunks]

        store_chunks(
            chunks=chunks,
            embeddings=embeddings,
            room_id=room_id,
            file_id=uploaded_file.id,
            filename=filename,
            file_type=extension
        )


        # 7. Update status
        uploaded_file.status = "ready"

        db.commit()


        # 8. Return response
        return {
            "file_id": uploaded_file.id,
            "chunks_created": len(chunks),
            "status": uploaded_file.status
        }


    except Exception as e:

        uploaded_file.status = "failed"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )
# changes start here
# Delete uploaded file route
@router.delete("/{room_id}/{file_id}")
def delete_uploaded_file(
    room_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Check room belongs to user
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
    ).first()


    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )


    # Find uploaded file
    uploaded_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.room_id == room_id
    ).first()


    if uploaded_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )


    # Delete physical file from uploads folder
    if os.path.exists(uploaded_file.file_path):

        os.remove(
            uploaded_file.file_path
        )


    # Delete database record
    db.delete(
        uploaded_file
    )

    db.commit()


    return {
        "message": "File deleted successfully"
    }