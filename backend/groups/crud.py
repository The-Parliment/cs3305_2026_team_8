from sqlalchemy.orm import Session
from models import GroupCreate
from schema import DBGroup

def create_group(db_handle: Session, new_group: GroupCreate):
    # An instance of a row to be put in the DB
    db_group = DBGroup(
        group_name = new_group.group_name, 
        group_desc = new_group.group_description, 
        is_private = new_group.is_private, 
        owner = new_group.owner 
    )

    # Now commit it.
    db_handle.add(db_group)
    db_handle.commit()

    #Refresh our db_groups FROM the DB so we can access the primary key created by the commit
    db_handle.refresh(db_group)
    return db_group.group_id
