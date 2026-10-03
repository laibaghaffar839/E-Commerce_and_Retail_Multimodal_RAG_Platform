from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.room import RoomCreate, RoomUpdate

from db.database import get_db
from db.models import ChatRoom, User
from services.auth import get_current_user

router = APIRouter(prefix="/rooms",tags=["Rooms"])

# get route
@router.get("/")
def get_rooms(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    rooms = db.query(ChatRoom).filter(
        ChatRoom.owner_id == current_user.id
    ).all()

    return rooms


# post route
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_room = ChatRoom(
        name=room_data.name,
        description=room_data.description,
        owner_id=current_user.id
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


# delete route
@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
    ).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    db.delete(room)
    db.commit()

    return {
        "message": "Room deleted successfully"
    }

# Change start here

# update route
@router.patch("/{room_id}")
def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
    ).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    if room_data.name is not None:
        room.name = room_data.name

    if room_data.description is not None:
        room.description = room_data.description

    db.commit()
    db.refresh(room)

    return room
