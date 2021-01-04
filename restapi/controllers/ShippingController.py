from config import database
from sqlalchemy.sql import select
from models.ShippingSubdistrictModel import shipping_subdistrict
from models.ShippingCityModel import shipping_city

class ShippingLogic:
    @staticmethod
    def extract_data_from_rajaongkir(data: dict) -> dict:
        results = dict()
        # get text origin details
        origin = data['rajaongkir']['origin_details']
        subdistrict = origin.get('subdistrict_name')
        city = origin.get('city') or origin.get('city_name')
        city_type = origin.get('type')
        city_origin = f"{city_type[:3] + '.' if city_type == 'Kabupaten' else city_type} {city}"
        city_origin = f"{city_origin + ', ' + subdistrict if subdistrict else city_origin}"
        results['origin_detail'] = city_origin
        # get text destination details
        origin = data['rajaongkir']['destination_details']
        subdistrict = origin.get('subdistrict_name')
        city = origin.get('city') or origin.get('city_name')
        city_type = origin.get('type')
        city_origin = f"{city_type[:3] + '.' if city_type == 'Kabupaten' else city_type} {city}"
        city_origin = f"{city_origin + ', ' + subdistrict if subdistrict else city_origin}"
        results['destination_detail'] = city_origin
        # set cost results
        results['costs_shipping'] = data['rajaongkir']['results']
        # min-max cost
        min_max_cost = list()
        for courier in [courier['costs'] for courier in results['costs_shipping']]:
            for cost in [cost['cost'] for cost in courier]:
                for v_cost in cost:
                    min_max_cost.append(v_cost['value'])

        results['min_cost'] = min(min_max_cost)
        results['max_cost'] = max(min_max_cost)

        return results

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
