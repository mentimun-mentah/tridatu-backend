from config import database
from sqlalchemy import func, desc
from sqlalchemy.sql import select, expression
from models.AddressModel import address
from models.PostalCodeModel import postal_code
from models.ProvinceModel import province
from libs.Pagination import Pagination

class AddressLogic:
    pass

class AddressCrud:
    @staticmethod
    async def create_address(**kwargs) -> int:
        return await database.execute(query=address.insert(),values=kwargs)

    @staticmethod
    async def update_address(id_: int, **kwargs) -> None:
        kwargs.update({"updated_at": func.now()})
        await database.execute(query=address.update().where(address.c.id == id_),values=kwargs)

    @staticmethod
    async def change_address_to_main_address(id_: int) -> None:
        await database.execute(query=address.update().where(address.c.id == id_),values={"main_address": True})

    @staticmethod
    async def delete_address(id_: int) -> None:
        await database.execute(query=address.delete().where(address.c.id == id_))

    @staticmethod
    async def change_all_main_address_to_false(user_id: int) -> None:
        query = select([address]).where((address.c.main_address == expression.true()) & (address.c.user_id == user_id))
        main_address_true = await database.fetch_all(query=query)
        for item in main_address_true:
            query = address.update().where(address.c.id == item['id'])
            await database.execute(query=query,values={'main_address': False})

    @staticmethod
    async def change_whatever_address_to_true(user_id: int) -> None:
        query = select([address]).where((address.c.main_address == expression.false()) & (address.c.user_id == user_id))
        if main_address_false := await database.fetch_one(query=query):
            query = address.update().where(address.c.id == main_address_false['id'])
            await database.execute(query=query,values={'main_address': True})

class AddressFetch:
    @staticmethod
    async def search_city_or_district(q: str) -> list:
        query = select([province.join(postal_code)]).where(
            postal_code.c.city.like("%" + q.upper() + "%") |
            postal_code.c.sub_district.like("%" + q.upper() + "%")
        ).distinct()
        # get data from database
        raw_data = await database.fetch_all(query=query)
        raw_data = [
            (f"{row['name']}, {row['city']}, {row['sub_district']}".title(),row['postal_code']) for row in raw_data
        ]
        # process data from the database for frontend
        data = []
        for row in sorted(set(raw_data)):
            if val := list(filter(lambda x: x['value'] == row[0], data)):
                val[0]['postal_code'].append(row[1])
            else:
                data.append({"value": row[0],"postal_code": [row[1]]})

        return data

    @staticmethod
    async def get_all_address_paginate(user_id: int, page: int, per_page: int) -> dict:
        query = select([func.count(address.c.id)]).where(address.c.user_id == user_id).as_scalar()
        total = await database.execute(query=query)

        query = select([address]).where(address.c.user_id == user_id) \
            .order_by(desc(address.c.main_address)).order_by(address.c.id) \
            .limit(per_page).offset((page - 1) * per_page)
        items = await database.fetch_all(query=query)

        paginate = Pagination(page, per_page, total, items)
        return {
            "data": [{index:value for index,value in item.items()} for item in paginate.items],
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }

    @staticmethod
    async def check_main_address_true_in_db(user_id: int) -> int:
        query = select([func.count(address.c.id)]) \
            .where((address.c.main_address == expression.true()) & (address.c.user_id == user_id)).as_scalar()
        return await database.execute(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> address:
        query = select([address]).where(address.c.id == id_)
        return await database.fetch_one(query=query)
