from sqlalchemy.orm import Session
from datetime import datetime
from common.db.structures.structures import Group, GroupJoin  # Import Group from common structures
from sqlalchemy import select
from models import GroupCreate, GroupsList, Group as PydanticGroup # Needed this last one because of nameclash with sqlalchemy model.


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
        group_desc=new_group.group_desc,
        is_private=new_group.is_private,
        owner=new_group.owner
    )
    
    # Commit to database
    db_handle.add(db_group)
    db_handle.commit()
    
    # Refresh to get the auto-generated primary key
    db_handle.refresh(db_group)
    # Use sqlalchemy magic to auto convert into the pydantic world
    return PydanticGroup.model_validate(db_group)

def join_group(db_handle: Session, join_handle: GroupJoin) -> bool:
    try:
        db_join = GroupMembers(
            group_id=join_handle.group_id,
            username=join_handle.username,
            date_joined=datetime.utcnow()
        )
        db_handle.add(db_join)
        db_handle.commit()
        return True

    # If there is any issues with the foreign key the
    # db will raise an exception
    # most likely we tried with a usename or groupd that does not exist.
    except IntegrityError:
        db_handle.rollback()
        return False

def list_all_groups(db_handle: Session):
    result = db_handle.execute(select(Group)).scalars().all()
    return GroupsList(group_list=result)
