from sqlalchemy.orm import Session
from sqlalchemy import select
from models import GroupCreate
from common.db.structures.structures import Group  # Import Group from common structures


def create_group(db_handle: Session, new_group: GroupCreate):
    """
    Create a new group in the database using the shared database structure.
    
    Args:
        db_handle: SQLAlchemy database session
        new_group: GroupCreate model with group details
        
    Returns:
        group_id: The ID of the newly created group
    """
    # Create an instance of a row to be put in the DB
    # Note: Adjust the Group constructor based on how it's defined in common/db/structures/structures.py
    db_group = Group(
        group_name=new_group.group_name,
        group_desc=new_group.group_description,
        is_private=new_group.is_private,
        owner=new_group.owner
    )
    
    # Commit to database
    db_handle.add(db_group)
    db_handle.commit()
    
    # Refresh to get the auto-generated primary key
    db_handle.refresh(db_group)
    
    return db_group.group_id

def list_all_groups(db_handle: Session):
    result = db_handle.execute(select(Group)).scalars().all()
    return result
