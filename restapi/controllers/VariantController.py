import json, uuid
from config import redis_conn, database
# from sqlalchemy.sql import select
from models.VariantModel import variant

class VariantLogic:
    def convert_data_to_db(variant_data: dict, product_id: int) -> list:
        variant_db = list()

        for variant_item in variant_data['va1_items']:
            if 'va1_name' not in variant_data:
                # without variant
                va1_code = variant_item['va1_code'] if 'va1_code' in variant_item else None
                va1_barcode = variant_item['va1_barcode'] if 'va1_barcode' in variant_item else None
                variant_db.append({
                    'price_variant': variant_item['va1_price'],
                    'stock_variant': variant_item['va1_stock'],
                    'code_variant': va1_code,
                    'barcode_variant': va1_barcode,
                    'product_id': product_id
                })
            elif 'va2_name' in variant_data:
                # double variant
                va1_image = variant_item['va1_image'] if 'va1_image' in variant_item else None
                for variant_two in variant_item['va2_items']:
                    va2_code = variant_two['va2_code'] if 'va2_code' in variant_two else None
                    va2_barcode = variant_two['va2_barcode'] if 'va2_barcode' in variant_two else None
                    variant_db.append({
                        'name_variant': '{}:{}'.format(variant_data['va1_name'],variant_data['va2_name']),
                        'option_variant': '{}:{}'.format(variant_item['va1_option'],variant_two['va2_option']),
                        'price_variant': variant_two['va2_price'],
                        'stock_variant': variant_two['va2_stock'],
                        'code_variant': va2_code,
                        'barcode_variant': va2_barcode,
                        'image_variant': va1_image,
                        'product_id': product_id
                    })
            else:
                # single variant
                va1_code = variant_item['va1_code'] if 'va1_code' in variant_item else None
                va1_barcode = variant_item['va1_barcode'] if 'va1_barcode' in variant_item else None
                va1_image = variant_item['va1_image'] if 'va1_image' in variant_item else None
                variant_db.append({
                    'name_variant': variant_data['va1_name'],
                    'option_variant': variant_item['va1_option'],
                    'price_variant': variant_item['va1_price'],
                    'stock_variant': variant_item['va1_stock'],
                    'code_variant': va1_code,
                    'barcode_variant': va1_barcode,
                    'image_variant': va1_image,
                    'product_id': product_id
                })

        return variant_db

class VariantCrud:
    async def create_variant(variant_db: list) -> None:
        await database.execute_many(query=variant.insert(),values=variant_db)

    def add_variant_to_redis_storage(data_variant: dict) -> str:
        ticket = str(uuid.uuid4())
        redis_conn.set(ticket, json.dumps(data_variant), 300)  # set expired 5 minutes
        return ticket

class VariantFetch:
    pass
