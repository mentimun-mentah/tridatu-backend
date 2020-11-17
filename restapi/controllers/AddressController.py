from config import database
from sqlalchemy import func
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
    async def check_and_change_main_address_to_false(user_id: int) -> None:
        query = select([address]).where((address.c.main_address == expression.true()) & (address.c.user_id == user_id))
        main_address_true = await database.fetch_all(query=query)
        for item in main_address_true:
            query = address.update().where(address.c.id == item['id'])
            await database.execute(query=query,values={'main_address': False})

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
            (f"{row['name']}, Kota {row['city']}, {row['sub_district']}".title(),row['postal_code']) for row in raw_data
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
    async def get_address_by_user_id(user_id: int, page: int, per_page: int) -> dict:
        query = select([func.count(address.c.id)]).where(address.c.user_id == user_id).as_scalar()
        total = await database.execute(query=query)

        query = select([address]) \
            .where((address.c.id > (((page - 1) * per_page) + 1)) & (address.c.user_id == user_id)) \
            .limit(per_page)
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
