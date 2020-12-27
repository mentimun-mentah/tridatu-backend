import json, uuid
from config import redis_conn, database
# from sqlalchemy.sql import select
from models.VariantModel import variant

class VariantLogic:
    @staticmethod
    def convert_data_to_db(variant_data: dict, product_id: int) -> list:
        variant_db = list()

        for variant_item in variant_data['va1_items']:
            if 'va1_name' not in variant_data:
                # without variant
                va1_code = variant_item['va1_code'] if 'va1_code' in variant_item else None
                va1_barcode = variant_item['va1_barcode'] if 'va1_barcode' in variant_item else None
                variant_db.append({
                    'price': variant_item['va1_price'],
                    'stock': variant_item['va1_stock'],
                    'code': va1_code,
                    'barcode': va1_barcode,
                    'product_id': product_id
                })
            elif 'va2_name' in variant_data:
                # double variant
                va1_image = variant_item['va1_image'] if 'va1_image' in variant_item else None
                for variant_two in variant_item['va2_items']:
                    va2_code = variant_two['va2_code'] if 'va2_code' in variant_two else None
                    va2_barcode = variant_two['va2_barcode'] if 'va2_barcode' in variant_two else None
                    variant_db.append({
                        'name': '{}:{}'.format(variant_data['va1_name'],variant_data['va2_name']),
                        'option': '{}:{}'.format(variant_item['va1_option'],variant_two['va2_option']),
                        'price': variant_two['va2_price'],
                        'stock': variant_two['va2_stock'],
                        'code': va2_code,
                        'barcode': va2_barcode,
                        'image': va1_image,
                        'product_id': product_id
                    })
            else:
                # single variant
                va1_code = variant_item['va1_code'] if 'va1_code' in variant_item else None
                va1_barcode = variant_item['va1_barcode'] if 'va1_barcode' in variant_item else None
                va1_image = variant_item['va1_image'] if 'va1_image' in variant_item else None
                variant_db.append({
                    'name': variant_data['va1_name'],
                    'option': variant_item['va1_option'],
                    'price': variant_item['va1_price'],
                    'stock': variant_item['va1_stock'],
                    'code': va1_code,
                    'barcode': va1_barcode,
                    'image': va1_image,
                    'product_id': product_id
                })

        return variant_db

    @staticmethod
    def convert_db_to_data(variant_db: list) -> list:
        # create class to store variable
        Record = type('Record', (object,), {'content':{}})
        duplicate_id = list(set([v.get('product_id') or v.get('variants_product_id') for v in variant_db]))

        result = list()
        for id_ in duplicate_id:
            tmp = dict()
            for item in variant_db:
                if id_ == (item.get('product_id') or item.get('variants_product_id')):
                    var = Record()
                    # initial variable with apply_labels or not
                    if item.get('variants_id') is None:
                        [var.__setattr__('v_{}'.format(key),item.get(key)) for key in item]
                    else:
                        [var.__setattr__('v_{}'.format('_'.join(key.split('_')[1:])),item.get(key)) for key in item]
                    var = var.__dict__

                    # without variant
                    if var['v_name'] is None:
                        tmp.update({
                            'va1_product_id': var['v_product_id'],
                            'va1_items': [{
                                'va1_id': var['v_id'],
                                'va1_price': var['v_price'],
                                'va1_stock': var['v_stock'],
                                'va1_code': var['v_code'],
                                'va1_barcode': var['v_barcode']
                            }]
                        })
                    # single variant
                    elif var['v_name'] and len(var['v_name'].split(':')) != 2:
                        v1_items = {
                            'va1_id': var['v_id'],
                            'va1_option': var['v_option'],
                            'va1_price': var['v_price'],
                            'va1_stock': var['v_stock'],
                            'va1_code': var['v_code'],
                            'va1_barcode': var['v_barcode'],
                            'va1_image': var['v_image']
                        }
                        if len(tmp) == 0:
                            tmp.update({
                                'va1_name': var['v_name'],
                                'va1_product_id': var['v_product_id'],
                                'va1_items': [v1_items]
                            })
                        else: tmp['va1_items'].append(v1_items)
                    # double variant
                    else:
                        v1_option = var['v_option'].split(':')[0]
                        v2_option = var['v_option'].split(':')[-1]
                        v1_image = var['v_image']
                        v2_items = {
                            'va2_id': var['v_id'],
                            'va2_option': v2_option,
                            'va2_price': var['v_price'],
                            'va2_stock': var['v_stock'],
                            'va2_code': var['v_code'],
                            'va2_barcode': var['v_barcode'],
                        }
                        if len(tmp) == 0:
                            tmp.update({
                                'va1_name': var['v_name'].split(':')[0],
                                'va2_name': var['v_name'].split(':')[-1],
                                'va1_product_id': var['v_product_id'],
                                'va1_items': [{
                                    'va1_option': v1_option,
                                    'va1_image': v1_image,
                                    'va2_items': [v2_items]
                                }]
                            })
                        else:
                            if v1_option not in [v['va1_option'] for v in tmp['va1_items']]:
                                tmp['va1_items'].append({
                                    'va1_option': v1_option,
                                    'va1_image': v1_image,
                                    'va2_items': [v2_items]
                                })
                            else:
                                # search index va1_items
                                idx = [i for i,v in enumerate(tmp['va1_items']) if v['va1_option'] == v1_option][0]
                                tmp['va1_items'][idx]['va2_items'].append(v2_items)

            result.append(tmp)
        return result

class VariantCrud:
    @staticmethod
    async def create_variant(variant_db: list) -> None:
        await database.execute_many(query=variant.insert(),values=variant_db)

    @staticmethod
    def add_variant_to_redis_storage(data_variant: dict) -> str:
        ticket = str(uuid.uuid4())
        redis_conn.set(ticket, json.dumps(data_variant), 300)  # set expired 5 minutes
        return ticket

class VariantFetch:
    pass
