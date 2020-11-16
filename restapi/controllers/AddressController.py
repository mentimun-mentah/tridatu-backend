from config import database
from sqlalchemy.sql import select
from models.PostalCodeModel import postal_code
from models.ProvinceModel import province

class AddressLogic:
    pass

class AddressCrud:
    pass

class AddressFetch:
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
