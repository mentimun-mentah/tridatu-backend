import json, uuid
from config import redis_conn, database
from sqlalchemy.sql import select
from models.VariantModel import variant
from typing import Union, Literal

class VariantLogic:
    @staticmethod
    def convert_data_to_db(variant_data: dict, product_id: Union[int,str]) -> list:
        variant_db = list()

        for variant_item in variant_data['va1_items']:
            if 'va1_name' not in variant_data:
                # without variant
                va1_code = variant_item['va1_code'] if 'va1_code' in variant_item else None
                va1_barcode = variant_item['va1_barcode'] if 'va1_barcode' in variant_item else None
                va1_data = {
                    'price': int(variant_item['va1_price']),
                    'stock': int(variant_item['va1_stock']),
                    'code': va1_code,
                    'barcode': va1_barcode,
                    'discount': 0,
                    'discount_active': False,
                    'product_id': int(product_id)
                }
                if 'va1_discount' in variant_item and 'va1_discount_active' in variant_item:
                    va1_data.update({'discount': variant_item['va1_discount'], 'discount_active': variant_item['va1_discount_active']})
                if 'va1_id' in variant_item:
                    va1_data.update({'id': int(variant_item['va1_id'])})

                variant_db.append(va1_data)
            elif 'va2_name' in variant_data:
                # double variant
                va1_image = variant_item['va1_image'] if 'va1_image' in variant_item else None
                for variant_two in variant_item['va2_items']:
                    va2_code = variant_two['va2_code'] if 'va2_code' in variant_two else None
                    va2_barcode = variant_two['va2_barcode'] if 'va2_barcode' in variant_two else None
                    va2_data = {
                        'name': '{}:{}'.format(variant_data['va1_name'],variant_data['va2_name']),
                        'option': '{}:{}'.format(variant_item['va1_option'],variant_two['va2_option']),
                        'price': int(variant_two['va2_price']),
                        'stock': int(variant_two['va2_stock']),
                        'code': va2_code,
                        'barcode': va2_barcode,
                        'image': va1_image,
                        'discount': 0,
                        'discount_active': False,
                        'product_id': int(product_id)
                    }
                    if 'va2_discount' in variant_two and 'va2_discount_active' in variant_two:
                        va2_data.update({'discount': variant_two['va2_discount'], 'discount_active': variant_two['va2_discount_active']})
                    if 'va2_id' in variant_two:
                        va2_data.update({'id': int(variant_two['va2_id'])})

                    variant_db.append(va2_data)
            else:
                # single variant
                va1_code = variant_item['va1_code'] if 'va1_code' in variant_item else None
                va1_barcode = variant_item['va1_barcode'] if 'va1_barcode' in variant_item else None
                va1_image = variant_item['va1_image'] if 'va1_image' in variant_item else None
                va1_data = {
                    'name': variant_data['va1_name'],
                    'option': variant_item['va1_option'],
                    'price': int(variant_item['va1_price']),
                    'stock': int(variant_item['va1_stock']),
                    'code': va1_code,
                    'barcode': va1_barcode,
                    'image': va1_image,
                    'discount': 0,
                    'discount_active': False,
                    'product_id': int(product_id)
                }
                if 'va1_discount' in variant_item and 'va1_discount_active' in variant_item:
                    va1_data.update({'discount': variant_item['va1_discount'], 'discount_active': variant_item['va1_discount_active']})
                if 'va1_id' in variant_item:
                    va1_data.update({'id': int(variant_item['va1_id'])})

                variant_db.append(va1_data)

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
                            'va1_product_id': str(var['v_product_id']),
                            'va1_items': [{
                                'va1_id': str(var['v_id']),
                                'va1_price': str(var['v_price']),
                                'va1_stock': str(var['v_stock']),
                                'va1_code': var['v_code'],
                                'va1_barcode': var['v_barcode'],
                                'va1_discount': var['v_discount'],
                                'va1_discount_active': var['v_discount_active']
                            }]
                        })
                    # single variant
                    elif var['v_name'] and len(var['v_name'].split(':')) != 2:
                        v1_items = {
                            'va1_id': str(var['v_id']),
                            'va1_option': var['v_option'],
                            'va1_price': str(var['v_price']),
                            'va1_stock': str(var['v_stock']),
                            'va1_code': var['v_code'],
                            'va1_barcode': var['v_barcode'],
                            'va1_discount': var['v_discount'],
                            'va1_discount_active': var['v_discount_active'],
                            'va1_image': var['v_image']
                        }
                        if len(tmp) == 0:
                            tmp.update({
                                'va1_name': var['v_name'],
                                'va1_product_id': str(var['v_product_id']),
                                'va1_items': [v1_items]
                            })
                        else: tmp['va1_items'].append(v1_items)
                    # double variant
                    else:
                        v1_option = var['v_option'].split(':')[0]
                        v2_option = var['v_option'].split(':')[-1]
                        v1_image = var['v_image']
                        v2_items = {
                            'va2_id': str(var['v_id']),
                            'va2_option': v2_option,
                            'va2_price': str(var['v_price']),
                            'va2_stock': str(var['v_stock']),
                            'va2_code': var['v_code'],
                            'va2_barcode': var['v_barcode'],
                            'va2_discount': var['v_discount'],
                            'va2_discount_active': var['v_discount_active'],
                        }
                        if len(tmp) == 0:
                            tmp.update({
                                'va1_name': var['v_name'].split(':')[0],
                                'va2_name': var['v_name'].split(':')[-1],
                                'va1_product_id': str(var['v_product_id']),
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

    @staticmethod
    def convert_type_data_variant(variant_data: dict, type_data: Literal['str','int'] = 'str') -> dict:
        if type_data == 'str': cnv = str
        elif type_data == 'int': cnv = int
        else: raise TypeError("type_data must be between str or int")

        if 'va1_product_id' in variant_data and variant_data['va1_product_id'] is not None:
            variant_data.update({'va1_product_id':cnv(variant_data['va1_product_id'])})

        for va1_items in variant_data['va1_items']:
            # update type data for va1_items
            {
                va1_items.update({key:cnv(value)}) for key,value in va1_items.copy().items()
                if value is not None and key in ['va1_id','va1_price','va1_stock']
            }

            # update type data for va2_items if exists
            if 'va2_items' in va1_items:
                for va2_items in va1_items['va2_items']:
                    {
                        va2_items.update({key:cnv(value)}) for key,value in va2_items.copy().items()
                        if value is not None and key in ['va2_id','va2_price','va2_stock']
                    }

        return variant_data

class VariantCrud:
    @staticmethod
    async def create_variant(variant_db: list) -> None:
        await database.execute_many(query=variant.insert(),values=variant_db)

    @staticmethod
    async def delete_variant(product_id: int) -> None:
        await database.execute(query=variant.delete().where(variant.c.product_id == product_id))

    @staticmethod
    async def update_variant(variant_db: list) -> None:
        [await database.execute(query=variant.update().where(variant.c.id == data['id']),values=data) for data in variant_db]

    @staticmethod
    async def delete_variant_by_id(variant_id: list) -> None:
        await database.execute(query=variant.delete().where(variant.c.id.in_(variant_id)))

    @staticmethod
    def add_variant_to_redis_storage(data_variant: dict) -> str:
        ticket = str(uuid.uuid4())
        redis_conn.set(ticket, json.dumps(data_variant), 300)  # set expired 5 minutes
        return ticket

class VariantFetch:
    @staticmethod
    async def get_produt_variant_id(product_id: int) -> list:
        query = select([variant.c.id]).where(variant.c.product_id == product_id)
        variant_db = await database.fetch_all(query=query)
        return [item['id'] for item in variant_db]

    @staticmethod
    async def get_product_variant_image(product_id: int) -> list:
        query = select([variant.c.image]).where(variant.c.product_id == product_id)
        variant_db = await database.fetch_all(query=query)
        variant_image = [item['image'] for item in variant_db if item['image']]

        return [v for i,v in enumerate(variant_image) if variant_image[i] not in variant_image[i + 1:]]

    @staticmethod
    async def get_variant_by_product_id(product_id: int) -> list:
        query = select([variant]).where(variant.c.product_id == product_id)
        variant_db = await database.fetch_all(query=query)
        variant_data = sorted(
            [{index:value for index,value in item.items()} for item in variant_db], key=lambda v: v['id']
        )
        return VariantLogic.convert_db_to_data(variant_data)[0]

    @staticmethod
    async def filter_by_id(id_: int) -> variant:
        query = select([variant]).where(variant.c.id == id_)
        return await database.fetch_one(query=query)
