from sqlalchemy import select,update,delete
from database.models import Info, Members
from sqlalchemy.ext.asyncio import AsyncSession

async def orm_add_info(session:AsyncSession,data:dict):
    obj=Info(
        name=data["name"],
        description=data["description"],
        image=data["image"],
    )
    session.add(obj)
    await session.commit()

async def orm_get_info(session:AsyncSession):
    query = select(Info)
    result=await session.execute(query)
    return result.scalars().all()

async def orm_get_one_info(session:AsyncSession,info_id:int):
    query = select(Info).where(Info.id==info_id)
    result=await session.execute(query)
    return result.scalar()

async def orm_update_info(session: AsyncSession, info_id: int, data):
    query = update(Info).where(Info.id == info_id).values(
        name=data["name"],
        description=data["description"],
        image=data["image"],)
    await session.execute(query)
    await session.commit()


async def orm_delete_info(session: AsyncSession, info_id: int):
    query = delete(Info).where(Info.id == info_id)
    await session.execute(query)
    await session.commit()

async def orm_add_member(session:AsyncSession,data:dict):
    obj=Members(
        name=data["name"],
        surname=data["surname"],
        team=data["team"],
        mark=data.get("mark"),
        id_user=data["id_user"]
    )
    session.add(obj)
    await session.commit()
    
async def orm_update_member(session: AsyncSession, member_id: int, member_mark:int):
    query = update(Members).where(Members.id == member_id).values(
        mark=member_mark,)
    await session.execute(query)
    await session.commit()

async def orm_get_member_by_name(session:AsyncSession,start_name:str):
    query = select(Members).where(Members.name.like(f"{start_name}%"))
    result=await session.execute(query)
    return result.scalars().all()

async def orm_get_member_mark(session:AsyncSession,member_id:int):
    query = select(Members).where(Members.id_user==member_id)
    result=await session.execute(query)
    return result.scalar()

async def orm_get_all_members(session:AsyncSession):
    query = select(Members.id_user)
    result=await session.execute(query)
    return result.scalars().all()