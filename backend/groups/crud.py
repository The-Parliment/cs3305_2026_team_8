from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from common.db.structures.structures import Group as DBGroup, GroupMembers  # Import Group from common structures
from sqlalchemy import select
from models import GroupCreate, GroupsList, GroupJoin, GroupLeave, GroupMembersList, GroupMemberInfo, Group as PydanticGroup # Needed this last one because of nameclash with sqlalchemy model.
import logging

logging.basicConfig(level=logging.INFO, format='[groups] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

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
    db_group = DBGroup(
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

def db_join_group(db_handle: Session, join_handle: GroupJoin) -> bool:
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
    except IntegrityError as e:
        db_handle.rollback()
        logger.error(f"IntegrityError: {e}")
        return False
    except Exception as e:
        db_handle.rollback()
        logger.error(f"Unexpected error: {e}")
        raise
    
def list_all_groups(db_handle: Session):
    result = db_handle.execute(select(DBGroup)).scalars().all()
    print(f"RAW RESULT: {result}")
    print(f"COUNT: {len(result)}")
    return GroupsList(group_list=result)

def my_groups(db_handle: Session, my_groups_handle):
    result = db_handle.execute(
        select(DBGroup)
        .join(GroupMembers, DBGroup.group_id == GroupMembers.group_id)
        .where(GroupMembers.username == my_groups_handle.username)
    ).scalars().all()
    return GroupsList(group_list=result)


def leave_group(db_handle: Session, join_handle: GroupLeave) -> bool:
    try:
        db_member = db_handle.execute(
                select(GroupMembers).where(
                GroupMembers.group_id == join_handle.group_id,
                GroupMembers.username == join_handle.username
            )
        ).scalar_one_or_none()

        if db_member is None:
            return True # Strange, but end result is the mapping does not exist in db, so we can consider the user as having "left" the group already.

        db_handle.delete(db_member)
        db_handle.commit()
        return True
    except Exception as e:
        db_handle.rollback()
        logger.error(f"Unexpected error: {e}")
        raise

def is_member(db_handle: Session, group_id: int, username: str) -> bool:
    result = db_handle.execute(
        select(GroupMembers).where(
            GroupMembers.group_id == group_id,
            GroupMembers.username == username
        )
    ).scalar_one_or_none()
    return result is not None

def list_members(db_handle: Session, group_id: int):
    result = db_handle.execute(
        select(GroupMembers).where(GroupMembers.group_id == group_id)
    ).scalars().all()
    return GroupMembersList(members=[GroupMemberInfo(username=m.username) for m in result])