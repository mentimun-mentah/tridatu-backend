from config import database
from sqlalchemy.sql import select
from models.ShippingSubdistrictModel import shipping_subdistrict
from models.ShippingCityModel import shipping_city

class ShippingFetch:
    @staticmethod
    async def search_shipping_city_or_district(q: str, limit: int) -> list:
        query = select([shipping_city.join(shipping_subdistrict)]) \
            .where(shipping_city.c.name.ilike(f"%{q}%") | (shipping_subdistrict.c.name.ilike(f"%{q}%"))) \
            .limit(limit).apply_labels()
        shipping_db = await database.fetch_all(query=query)
        shipping_data = [
            {
                'value': f"{item['shipping_cities_type'][:3] + '.' if item['shipping_cities_type'] == 'Kabupaten' else item['shipping_cities_type']} {item['shipping_cities_name']}, {item['shipping_subdistricts_name']}",
                'shipping_cities_id': item['shipping_cities_id'],
                'shipping_subdistricts_id': item['shipping_subdistricts_id']
            }
            for item in [{index:value for index,value in item.items()} for item in shipping_db]
        ]
        return shipping_data
