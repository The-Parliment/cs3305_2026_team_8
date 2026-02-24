from sqlalchemy.exc import IntegrityError
from datetime import datetime
from common.db.structures.structures import Group as DBGroup, GroupMembers  # Import Group from common structures
from common.db.db import get_db
from sqlalchemy import select
from models import GroupCreate, GroupsList, GroupJoin, GroupLeave, GroupMembersList, GroupMemberInfo, Group as PydanticGroup # Needed this last one because of nameclash with sqlalchemy model.
import logging

logging.basicConfig(level=logging.INFO, format='[groups] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def create_group(new_group: GroupCreate):
    """
    Create a new group in the database using the shared database structure.
    
    Args:
        db_handle: SQLAlchemy database session
        new_group: GroupCreate model with group details
        
    Returns:
        group_id: The ID of the newly created group
    """
    with get_db() as db:
        # Create an instance of a row to be put in the DB
        # Note: Adjust the Group constructor based on how it's defined in common/db/structures/structures.py
        db_group = DBGroup(
            group_name=new_group.group_name,
            group_desc=new_group.group_desc,
            is_private=new_group.is_private,
            owner=new_group.owner
        )

        # Commit to database
        db.add(db_group)
        db.commit()

        # Refresh to get the auto-generated primary key
        db.refresh(db_group)
        # Use sqlalchemy magic to auto convert into the pydantic world
        return PydanticGroup.model_validate(db_group)

def db_join_group(join_handle: GroupJoin) -> bool:
    with get_db() as db:
        try:
            db_join = GroupMembers(
                group_id=join_handle.group_id,
                username=join_handle.username,
                date_joined=datetime.utcnow()
            )
            db.add(db_join)
            db.commit()
            return True

        # If there is any issues with the foreign key the
        # db will raise an exception
        # most likely we tried with a usename or groupd that does not exist.
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError: {e}")
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error: {e}")
            raise
    
def list_all_groups():
    with get_db() as db:
        result = db.execute(select(DBGroup)).scalars().all()
        print(f"RAW RESULT: {result}")
        print(f"COUNT: {len(result)}")
        return GroupsList(group_list=result)

def my_groups(my_groups_handle):
    with get_db() as db:
        result = db.execute(
            select(DBGroup)
            .join(GroupMembers, DBGroup.group_id == GroupMembers.group_id)
            .where(GroupMembers.username == my_groups_handle.username)
        ).scalars().all()
        return GroupsList(group_list=result)


def leave_group(join_handle: GroupLeave) -> bool:
    with get_db() as db:
        try:
            db_member = db.execute(
                    select(GroupMembers).where(
                    GroupMembers.group_id == join_handle.group_id,
                    GroupMembers.username == join_handle.username
                )
            ).scalar_one_or_none()

            if db_member is None:
                return True # Strange, but end result is the mapping does not exist in db, so we can consider the user as having "left" the group already.

            db.delete(db_member)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error: {e}")
            raise

def is_member(group_id: int, username: str) -> bool:
    with get_db() as db:
        result = db.execute(
            select(GroupMembers).where(
                GroupMembers.group_id == group_id,
                GroupMembers.username == username
            )
        ).scalar_one_or_none()
        return result is not None

def list_members(group_id: int):
    with get_db() as db:
        result = db.execute(
            select(GroupMembers).where(GroupMembers.group_id == group_id)
        ).scalars().all()
        return GroupMembersList(members=[GroupMemberInfo(username=m.username) for m in result])