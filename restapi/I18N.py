PydanticError = {
    'en': {
        'value_error.missing': 'field required',
        'value_error.extra': 'extra fields not permitted',
        'type_error.none.not_allowed': 'none is not an allowed value',
        'type_error.none.allowed': 'value is not none',
        'value_error.const': 'unexpected value; permitted: {permitted}',
        'type_error.not_none': 'value is not None',
        'type_error.bool': 'value could not be parsed to a boolean',
        'type_error.bytes': 'byte type expected',
        'type_error.dict': 'value is not a valid dict',
        'value_error.email': 'value is not a valid email address',
        'value_error.url.scheme': 'invalid or missing URL scheme',
        'value_error.url.userinfo': 'userinfo required in URL but missing',
        'value_error.url.host': 'URL host invalid',
        'value_error.url.port': 'URL port invalid, port cannot exceed 65535',
        'value_error.url.extra': 'URL invalid, extra characters found after valid URL: {extra!r}',
        'type_error.enum': 'value is not a valid enumeration member; permitted: {permitted}',
        'type_error.integer': 'value is not a valid integer',
        'type_error.float': 'value is not a valid float',
        'type_error.path': 'value is not a valid path',
        'value_error.path.not_exists': 'file or directory at path "{path}" does not exist',
        'value_error.path.not_a_file': 'path "{path}" does not point to a file',
        'value_error.path.not_a_directory': 'path "{path}" does not point to a directory',
        'type_error.pyobject': 'ensure this value contains valid import path or valid callable: {error_message}',
        'type_error.sequence': 'value is not a valid sequence',
        'type_error.iterable': 'value is not a valid iterable',
        'type_error.list': 'value is not a valid list',
        'type_error.set': 'value is not a valid set',
        'type_error.frozenset': 'value is not a valid frozenset',
        'type_error.deque': 'value is not a valid deque',
        'type_error.tuple': 'value is not a valid tuple',
        'value_error.tuple.length': 'wrong tuple length {actual_length}, expected {expected_length}',
        'value_error.list.min_items': 'ensure this value has at least {limit_value} items',
        'value_error.list.max_items': 'ensure this value has at most {limit_value} items',
        'value_error.set.min_items': 'ensure this value has at least {limit_value} items',
        'value_error.set.max_items': 'ensure this value has at most {limit_value} items',
        'value_error.any_str.min_length': 'ensure this value has at least {limit_value} characters',
        'value_error.any_str.max_length': 'ensure this value has at most {limit_value} characters',
        'type_error.str': 'str type expected',
        'value_error.str.regex': 'string does not match regex "{pattern}"',
        'value_error.number.not_gt': 'ensure this value is greater than {limit_value}',
        'value_error.number.not_ge': 'ensure this value is greater than or equal to {limit_value}',
        'value_error.number.not_lt': 'ensure this value is less than {limit_value}',
        'value_error.number.not_le': 'ensure this value is less than or equal to {limit_value}',
        'value_error.number.not_multiple': 'ensure this value is a multiple of {multiple_of}',
        'type_error.decimal': 'value is not a valid decimal',
        'value_error.decimal.not_finite': 'value is not a valid decimal',
        'value_error.decimal.max_digits': 'ensure that there are no more than {max_digits} digits in total',
        'value_error.decimal.max_places': 'ensure that there are no more than {decimal_places} decimal places',
        'value_error.decimal.whole_digits': 'ensure that there are no more than {whole_digits} digits before the decimal point',
        'value_error.datetime': 'invalid datetime format',
        'value_error.date': 'invalid date format',
        'value_error.time': 'invalid time format',
        'value_error.duration': 'invalid duration format',
        'type_error.hashable': 'value is not a valid hashable',
        'type_error.uuid': 'value is not a valid uuid',
        'value_error.uuid.version': 'uuid version {required_version} expected',
        'type_error.arbitrary_type': 'instance of {expected_arbitrary_type} expected',
        'type_error.class': 'a class is expected',
        'type_error.subclass': 'subclass of {expected_class} expected',
        'value_error.json': 'Invalid JSON',
        'type_error.json': 'JSON object must be str, bytes or bytearray',
        'value_error.regex_pattern': 'Invalid regular expression',
        'type_error.dataclass': 'instance of {class_name}, tuple or dict expected',
        'type_error.callable': '{value} is not callable',
        'type_error.enum_instance': '{value} is not a valid Enum instance',
        'type_error.int_enum_instance': '{value} is not a valid IntEnum instance',
        'value_error.ipvanyaddress': 'value is not a valid IPv4 or IPv6 address',
        'value_error.ipvanyinterface': 'value is not a valid IPv4 or IPv6 interface',
        'value_error.ipvanynetwork': 'value is not a valid IPv4 or IPv6 network',
        'value_error.ipv4address': 'value is not a valid IPv4 address',
        'value_error.ipv6address': 'value is not a valid IPv6 address',
        'value_error.ipv4network': 'value is not a valid IPv4 network',
        'value_error.ipv6network': 'value is not a valid IPv6 network',
        'value_error.ipv4interface': 'value is not a valid IPv4 interface',
        'value_error.ipv6interface': 'value is not a valid IPv6 interface',
        'value_error.color': 'value is not a valid color: {reason}',
        'value_error.strictbool': 'value is not a valid boolean',
        'value_error.payment_card_number.digits': 'card number is not all digits',
        'value_error.payment_card_number.luhn_check': 'card number is not luhn valid',
        'value_error.payment_card_number.invalid_length_for_brand': 'Length for a {brand} card must be {required_length}',
        'value_error.invalidbytesize': 'could not parse value and unit from byte string',
        'value_error.invalidbytesizeunit': 'could not interpret byte unit: {unit}',
        # custom error from app
        'value_error.phone_number': 'value is not a valid mobile phone number',
        'value_error.password_confirm': 'password must match with password confirmation',
        'value_error.discount_start.time': 'the start time must be after the current time',
        'value_error.discount_end.min_exp': 'the expiration time must be at least one hour longer than the start time',
        'value_error.discount_end.max_exp': 'promo period must be less than 180 days',
        'value_error.variant.duplicate_option': 'the option must be different with each other',
        'value_error.variant.duplicate_name': 'the name must be different with each other',
        'value_error.variant.name_one.missing': 'ensure va1_name value is not null',
        'value_error.variant.name_two.missing': 'ensure va2_name value is not null',
        'value_error.variant.product_id.missing': 'ensure va1_product_id value is not null',
        'value_error.variant.id_two.missing': 'ensure va2_id at option {option} and index {index} value is not null',
        'value_error.variant.discount_active_two.missing': 'ensure va2_discount_active at option {option} and index {index} value is not null',
        'value_error.variant.discount_two.missing': 'ensure va2_discount at option {option} and index {index} value is not null',
        'value_error.variant.discount_two.not_gt': 'ensure va2_discount at option {option} and index {index} value is greater than {limit_value}',
        'value_error.variant.id_one.without_index.missing': 'ensure va1_id value is not null',
        'value_error.variant.discount_active_one.without_index.missing': 'ensure va1_discount_active value is not null',
        'value_error.variant.discount_one.without_index.missing': 'ensure va1_discount value is not null',
        'value_error.variant.discount_one.without_index.not_gt': 'ensure va1_discount value is greater than {limit_value}',
        'value_error.variant.id_one.missing': 'ensure va1_id at index {index} value is not null',
        'value_error.variant.discount_active_one.missing': 'ensure va1_discount_active at index {index} value is not null',
        'value_error.variant.discount_one.missing': 'ensure va1_discount at index {index} value is not null',
        'value_error.variant.discount_one.not_gt': 'ensure va1_discount at index {index} value is greater than {limit_value}',
        'value_error.variant.option_one.missing': 'ensure va1_option at index {index} value is not null',
        'value_error.variant.price_one.missing': 'ensure va1_price at index {index} value is not null',
        'value_error.variant.stock_one.missing': 'ensure va1_stock at index {index} value is not null',
        'value_error.variant.price_one.without_index.missing': 'ensure va1_price value is not null',
        'value_error.variant.stock_one.without_index.missing': 'ensure va1_stock value is not null',
        'value_error.wholesale_variant.missing': 'variant not found',
        'value_error.wholesale_variant.not_same': 'wholesale prices are only available for all variant that are priced the same',
        'value_error.wholesale_price_initial.not_ge': 'price {idx}: The price shall not be 50% lower than the initial price',
        'value_error.wholesale_min_qty.not_gt': 'min_qty {idx}: must be more > than before',
        'value_error.wholesale_price.not_lt': 'price {idx}: The price must be less than the previous price'
    },
    'id': {
        'value_error.missing': 'inputan tidak boleh kosong',
        'value_error.extra': 'inputan tambahan tidak diizinkan',
        'type_error.none.not_allowed': 'none bukan value yang diperbolehkan',
        'type_error.none.allowed': 'value bukan none',
        'value_error.const': 'value tidak diizinkan; yang diizinkan: {permitted}',
        'type_error.not_none': 'value bukan None',
        'type_error.bool': 'value tidak bisa dijadikan boolean',
        'type_error.bytes': 'type data harus byte',
        'type_error.dict': 'value harus berupa dict',
        'value_error.email': 'value harus berupa alamat email',
        'value_error.url.scheme': 'skema URL tidak valid atau tidak ada',
        'value_error.url.userinfo': 'userinfo diperlukan di URL tetapi tidak ada',
        'value_error.url.host': 'host URL tidak valid',
        'value_error.url.port': 'port URL tidak valid, port tidak boleh melebihi 65535',
        'value_error.url.extra': 'URL tidak valid, karakter tambahan ditemukan setelah URL yang valid: {extra!r}',
        'type_error.enum': 'value bukan merupakan enumeration member; yang diizinkan: {permitted}',
        'type_error.integer': 'value harus berupa integer',
        'type_error.float': 'value harus berupa float',
        'type_error.path': 'value harus berupa path',
        'value_error.path.not_exists': 'file atau direktori di "{path}" tidak ada',
        'value_error.path.not_a_file': '"{path}" tidak merujuk pada file',
        'value_error.path.not_a_directory': '"{path}" tidak merujuk pada direktori',
        'type_error.pyobject': 'pastikan value mengandung import path atau callable yang benar: {error_message}',
        'type_error.sequence': 'value harus berupa sequence',
        'type_error.iterable': 'value harus berupa iterable',
        'type_error.list': 'value harus berupa list',
        'type_error.set': 'value harus berupa set',
        'type_error.frozenset': 'value harus berupa frozenset',
        'type_error.deque': 'value harus berupa deque',
        'type_error.tuple': 'value harus berupa tuple',
        'value_error.tuple.length': 'panjang tuple salah {actual_length}, diharapkan {expected_length}',
        'value_error.list.min_items': 'pastikan value ini memiliki setidaknya {limit_value} item',
        'value_error.list.max_items': 'pastikan value ini paling banyak {limit_value} item',
        'value_error.set.min_items': 'pastikan value ini memiliki setidaknya {limit_value} item',
        'value_error.set.max_items': 'pastikan value ini paling banyak {limit_value} item',
        'value_error.any_str.min_length': 'pastikan value ini memiliki setidaknya {limit_value} karakter',
        'value_error.any_str.max_length': 'pastikan value ini paling banyak {limit_value} karakter',
        'type_error.str': 'type data harus str',
        'value_error.str.regex': 'string tidak cocok dengan regex "{pattern}"',
        'value_error.number.not_gt': 'pastikan value ini lebih besar dari {limit_value}',
        'value_error.number.not_ge': 'pastikan value ini lebih besar atau sama dengan {limit_value}',
        'value_error.number.not_lt': 'pastikan value ini kurang dari {limit_value}',
        'value_error.number.not_le': 'pastikan value ini kurang dari atau sama dengan {limit_value}',
        'value_error.number.not_multiple': 'pastikan value ini adalah kelipatan {multiple_of}',
        'type_error.decimal': 'value harus berupa decimal',
        'value_error.decimal.not_finite': 'value harus berupa decimal',
        'value_error.decimal.max_digits': 'pastikan bahwa tidak lebih dari {max_digits} total digit',
        'value_error.decimal.max_places': 'pastikan bahwa tidak lebih dari {decimal_places} tempat decimal',
        'value_error.decimal.whole_digits': 'pastikan bahwa tidak lebih dari {whole_digits} digit sebelum koma',
        'value_error.datetime': 'format datetime tidak valid',
        'value_error.date': 'format date tidak valid',
        'value_error.time': 'format time tidak valid',
        'value_error.duration': 'format duration tidak valid',
        'type_error.hashable': 'value harus berupa hashable',
        'type_error.uuid': 'value harus berupa uuid',
        'value_error.uuid.version': 'versi uuid harus {required_version}',
        'type_error.arbitrary_type': 'instance harus {expected_arbitrary_type}',
        'type_error.class': 'type data harus class',
        'type_error.subclass': 'subclass harus {expected_class}',
        'value_error.json': 'JSON tidak valid',
        'type_error.json': 'objek JSON harus str, bytes atau bytearray',
        'value_error.regex_pattern': 'regular expression tidak valid',
        'type_error.dataclass': 'instance {class_name}, harus berupa tuple atau dict',
        'type_error.callable': '{value} bukan callable',
        'type_error.enum_instance': '{value} harus berupa Enum instance',
        'type_error.int_enum_instance': '{value} harus berupa IntEnum instance',
        'value_error.ipvanyaddress': 'value harus berupa IPv4 atau IPv6 address',
        'value_error.ipvanyinterface': 'value harus berupa IPv4 atau IPv6 interface',
        'value_error.ipvanynetwork': 'value harus berupa IPv4 atau IPv6 network',
        'value_error.ipv4address': 'value harus berupa IPv4 address',
        'value_error.ipv6address': 'value harus berupa IPv6 address',
        'value_error.ipv4network': 'value harus berupa IPv4 network',
        'value_error.ipv6network': 'value harus berupa IPv6 network',
        'value_error.ipv4interface': 'value harus berupa IPv4 interface',
        'value_error.ipv6interface': 'value harus berupa IPv6 interface',
        'value_error.color': 'value harus berupa warna: {reason}',
        'value_error.strictbool': 'value harus berupa boolean',
        'value_error.payment_card_number.digits': 'nomor kartu tidak semuanya digit',
        'value_error.payment_card_number.luhn_check': 'nomor kartu tidak luhn yang valid',
        'value_error.payment_card_number.invalid_length_for_brand': 'panjang untuk kartu {brand} harus {required_length}',
        'value_error.invalidbytesize': 'tidak dapat mengubah value dan unit dari byte string',
        'value_error.invalidbytesizeunit': 'tidak dapat menafsirkan byte unit: {unit}',
        # custom error from app
        'value_error.phone_number': 'value harus berupa nomor ponsel',
        'value_error.password_confirm': 'kata sandi harus sesuai dengan konfirmasi kata sandi',
        'value_error.discount_start.time': 'waktu mulai harus setelah waktu saat ini',
        'value_error.discount_end.min_exp': 'waktu kedaluwarsa setidaknya harus satu jam lebih lama dari waktu mulai',
        'value_error.discount_end.max_exp': 'periode promo harus kurang dari 180 hari',
        'value_error.variant.duplicate_option': 'opsi harus berbeda satu sama lain',
        'value_error.variant.duplicate_name': 'nama harus berbeda satu sama lain',
        'value_error.variant.name_one.missing': 'pastikan value va1_name tidak kosong',
        'value_error.variant.name_two.missing': 'pastikan value va2_name tidak kosong',
        'value_error.variant.product_id.missing': 'pastikan value va1_product_id tidak kosong',
        'value_error.variant.id_two.missing': 'pastikan value va2_id pada opsi {option} dan indeks {index} tidak kosong',
        'value_error.variant.discount_active_two.missing': 'pastikan value va2_discount_active pada opsi {option} dan indeks {index} tidak kosong',
        'value_error.variant.discount_two.missing': 'pastikan value va2_discount pada opsi {option} dan indeks {index} tidak kosong',
        'value_error.variant.discount_two.not_gt': 'pastikan value va2_discount pada opsi {option} dan indeks {index} lebih besar dari {limit_value}',
        'value_error.variant.id_one.without_index.missing': 'pastikan value va1_id tidak kosong',
        'value_error.variant.discount_active_one.without_index.missing': 'pastikan value va1_discount_active tidak kosong',
        'value_error.variant.discount_one.without_index.missing': 'pastikan value va1_discount tidak kosong',
        'value_error.variant.discount_one.without_index.not_gt': 'pastikan value va1_discount lebih besar dari {limit_value}',
        'value_error.variant.id_one.missing': 'pastikan value va1_id pada indeks {index} tidak kosong',
        'value_error.variant.discount_active_one.missing': 'pastikan value va1_discount_active pada indeks {index} tidak kosong',
        'value_error.variant.discount_one.missing': 'pastikan value va1_discount pada indeks {index} tidak kosong',
        'value_error.variant.discount_one.not_gt': 'pastikan value va1_discount pada indeks {index} lebih besar dari {limit_value}',
        'value_error.variant.option_one.missing': 'pastikan value va1_option pada indeks {index} tidak kosong',
        'value_error.variant.price_one.missing': 'pastikan value va1_price pada indeks {index} tidak kosong',
        'value_error.variant.stock_one.missing': 'pastikan value va1_stock pada indeks {index} tidak kosong',
        'value_error.variant.price_one.without_index.missing': 'pastikan value va1_price tidak kosong',
        'value_error.variant.stock_one.without_index.missing': 'pastikan value va1_stock tidak kosong',
        'value_error.wholesale_variant.missing': 'varian tidak ditemukan',
        'value_error.wholesale_variant.not_same': 'harga grosir hanya tersedia untuk semua varian dengan harga yang sama',
        'value_error.wholesale_price_initial.not_ge': 'harga {idx}: Harga tidak boleh 50% lebih rendah dari harga awal',
        'value_error.wholesale_min_qty.not_gt': 'min_qty {idx}: harus lebih > dari sebelumnya',
        'value_error.wholesale_price.not_lt': 'harga {idx}: Harga harus lebih kecil dari harga sebelumnya'
    }
}

ResponseMessages = {
    'en': {
        # address endpoint
        'create_address': {201: {"detail": "Successfully add a new address."}},
        'update_address': {200: {"detail": "Successfully update the address."}},
        'main_address_true': {200: {"detail": "Successfully set the address to main address."}},
        'delete_address': {200: {"detail": "Successfully delete the address."}},
        # brands endpoint
        'create_brand': {201: {"detail": "Successfully add a new brand."}},
        'update_brand': {200: {"detail": "Successfully update the brand."}},
        'delete_brand': {200: {"detail": "Successfully delete the brand."}},
        # carts endpoint
        'put_product_to_cart': {
            200: {"detail": "Shopping cart successfully updated."},
            201: {"detail": "The product has been successfully added to the shopping cart."}
        },
        'delete_cart': {200: {"detail": "{item} items were removed."}},
        'move_to_wishlist': {200: {"detail": "{item} items successfully moved to the wishlist."}},
        # categories endpoint
        'create_category': {201: {"detail": "Successfully add a new category."}},
        'update_category': {200: {"detail": "Successfully update the category."}},
        'delete_category': {200: {"detail": "Successfully delete the category."}},
        # comments endpoint
        'create_comment': {201: {"detail": "Comment successfully added."}},
        'delete_comment': {200: {"detail": "Comment successfully deleted."}},
        # discounts endpoint
        'create_discount_product': {201: {"detail": "Successfully set discount on product."}},
        'update_discount_product': {200: {"detail": "Successfully updated discount on product."}},
        'non_active_discount': {200: {"detail": "Successfully unset discount on the product."}},
        # item_sub_categories endpoint
        'create_item_sub_category': {201: {"detail": "Successfully add a new item-sub-category."}},
        'update_item_sub_category': {200: {"detail": "Successfully update the item-sub-category."}},
        'delete_item_sub_category': {200: {"detail": "Successfully delete the item-sub-category."}},
        # outlets endpoint
        'create_outlet': {201: {"detail": "Successfully add a new outlet."}},
        'delete_outlet': {200: {"detail": "Successfully delete the outlet."}},
        # products endpoint
        'create_product': {201: {"detail": "Successfully add a new product."}},
        'change_product_alive_archive': {200: {"detail": "Successfully change the product to {msg}."}},
        'update_product': {200: {"detail": "Successfully update the product."}},
        'delete_product': {200: {"detail": "Successfully delete the product."}},
        # replies endpoint
        'create_reply': {201: {"detail": "Successfully reply to this comment."}},
        'delete_reply': {200: {"detail": "Reply successfully deleted."}}
    },
    'id': {
        # address endpoint
        'create_address': {201: {"detail": "Berhasil menambahkan alamat baru."}},
        'update_address': {200: {"detail": "Berhasil memperbarui alamat."}},
        'main_address_true': {200: {"detail": "Berhasil mengatur alamat ke alamat utama."}},
        'delete_address': {200: {"detail": "Berhasil menghapus alamat."}},
        # brands endpoint
        'create_brand': {201: {"detail": "Berhasil menambahkan brand baru."}},
        'update_brand': {200: {"detail": "Berhasil memperbarui brand."}},
        'delete_brand': {200: {"detail": "Berhasil menghapus brand."}},
        # carts endpoint
        'put_product_to_cart': {
            200: {"detail": "Keranjang belanja berhasil diperbarui."},
            201: {"detail": "Produk telah berhasil ditambahkan ke keranjang belanjaan."}
        },
        'delete_cart': {200: {"detail": "{item} item telah dihapus."}},
        'move_to_wishlist': {200: {"detail": "{item} item berhasil dipindahkan ke wishlist."}},
        # categories endpoint
        'create_category': {201: {"detail": "Berhasil menambahkan kategori baru."}},
        'update_category': {200: {"detail": "Berhasil memperbarui kategori."}},
        'delete_category': {200: {"detail": "Berhasil menghapus kategori."}},
        # comments endpoint
        'create_comment': {201: {"detail": "Komentar berhasil ditambahkan."}},
        'delete_comment': {200: {"detail": "Komentar berhasil dihapus."}},
        # discounts endpoint
        'create_discount_product': {201: {"detail": "Berhasil menetapkan diskon pada produk."}},
        'update_discount_product': {200: {"detail": "Diskon produk berhasil diperbarui."}},
        'non_active_discount': {200: {"detail": "Berhasil membatalkan diskon pada produk."}},
        # item_sub_categories endpoint
        'create_item_sub_category': {201: {"detail": "Berhasil menambahkan item-sub-kategori baru."}},
        'update_item_sub_category': {200: {"detail": "Berhasil memperbarui item-sub-kategori."}},
        'delete_item_sub_category': {200: {"detail": "Berhasil menghapus item-sub-kategori."}},
        # outlets endpoint
        'create_outlet': {201: {"detail": "Berhasil menambahkan outlet baru."}},
        'delete_outlet': {200: {"detail": "Berhasil menghapus outlet."}},
        # products endpoint
        'create_product': {201: {"detail": "Berhasil menambahkan produk baru."}},
        'change_product_alive_archive': {200: {"detail": "Berhasil mengubah produk menjadi {msg}."}},
        'update_product': {200: {"detail": "Berhasil memperbarui produk."}},
        'delete_product': {200: {"detail": "Berhasil menghapus produk."}},
        # replies endpoint
        'create_reply': {201: {"detail": "Berhasil membalas komentar ini."}},
        'delete_reply': {200: {"detail": "Balasan berhasil dihapus."}}
    }
}

HttpError = {
    'en': {
        # user controller
        'user_controller.not_admin': {'message': 'Only users with admin privileges can do this action.', 'code': 'user_controller.not_admin'},
        'user_controller.not_found': {'message': 'User not found!', 'code': 'user_controller.not_found'},
        # magic image
        'single_image.not_lt': {'message': 'An image cannot greater than {max_file_size} Mb.', 'code': 'single_image.not_lt', 'ctx': {}},
        'single_image.not_img': {'message': 'Cannot identify the image.', 'code': 'single_image.not_img'},
        'single_image.ext.not_allowed': {'message': 'Image must be between {extension}.', 'code': 'single_image.ext.not_allowed', 'ctx': {}},
        'multiple_image.ext.not_allowed': {
            'message': 'The image at index {index} must be between {extension}.',
            'code': 'multiple_image.ext.not_allowed',
            'ctx': {}
        },
        'multiple_image.not_img': {'message': 'Cannot identify the image at index {index}.', 'code': 'multiple_image.not_img', 'ctx': {}},
        'multiple_image.not_lt': {
            'message': 'An image at index {index} cannot greater than {max_file_size} Mb.',
            'code': 'multiple_image.not_lt',
            'ctx': {}
        },
        'multiple_image.not_unique': {'message': 'Each image must be unique.', 'code': 'multiple_image.not_unique'},
        'multiple_image.min_items': {'message': 'At least {min_file_in_list} image must be upload.', 'code': 'multiple_image.min_items', 'ctx': {}},
        'multiple_image.max_items': {'message': 'Maximal {max_file_in_list} images to be upload.', 'code': 'multiple_image.max_items', 'ctx': {}},
        # address endpoint
        'address.not_found': {'message': 'Address not found!', 'code': 'address.not_found'},
        'address.not_match': {'message': 'Address not match with the current user.', 'code': 'address.not_match'},
        # brands endpoint
        'brands.name_taken': {'message': 'The name has already been taken.', 'code': 'brands.name_taken'},
        'brands.not_found': {'message': 'Brand not found!', 'code': 'brands.not_found'},
        # carts endpoint
        'carts.stock_not_enough_1': {'message': 'The amount you input exceeds the available stock.', 'code': 'carts.stock_not_enough_1'},
        'carts.stock_not_enough_2': {
            'message': 'This item has {stock} stock left and you already have {qty} in your basket.',
            'code': 'carts.stock_not_enough_2',
            'ctx': {}
        },
        'carts.max_items': {
            'message': 'The basket can only contain 20 items. Delete some items to add others.',
            'code': 'carts.max_items'
        },
        'carts.variant_not_found': {'message': 'Variant not found!', 'code': 'carts.variant_not_found'},
        # categories endpoint
        'categories.name_taken': {'message': 'The name has already been taken.', 'code': 'categories.name_taken'},
        'categories.not_found': {'message': 'Category not found!', 'code': 'categories.not_found'},
        # comments endpoint
        'comments.is_admin': {'message': 'Admin cannot create comments in their own product.', 'code': 'comments.is_admin'},
        'comments.product_not_found': {'message': 'Product not found!', 'code': 'comments.product_not_found'},
        'comments.cooldown': {
            'message': "You've already added comment a moment ago. Please try again later.",
            'code': 'comments.cooldown'
        },
        'comments.not_match': {'message': 'Comment not match with the current user.', 'code': 'comments.not_match'},
        'comments.not_found': {'message': 'Comment not found!', 'code': 'comments.not_found'},
        # discounts endpoint
        'discounts.product_not_found': {'message': 'Product not found!', 'code': 'discounts.product_not_found'},
        'discounts.variant_not_found': {'message': 'Ticket variant not found!', 'code': 'discounts.variant_not_found'},
        'discounts.has_discount': {'message': 'Product already has discount.', 'code': 'discounts.has_discount'},
        'discounts.variant_not_same': {'message': 'Variant not same with product.', 'code': 'discounts.variant_not_same'},
        'discounts.missing': {'message': 'You must set a discount on the product before update it.', 'code': 'discounts.missing'},
        'discounts.start_time': {'message': 'The new start time must be after the set start time.', 'code': 'discounts.start_time'},
        'discounts.min_exp': {'message': 'The expiration time must be at least one hour longer than the start time.', 'code': 'discounts.min_exp'},
        'discounts.max_exp': {'message': 'Promo period must be less than 180 days.', 'code': 'discounts.max_exp'},
        # item_sub_categories endpoint
        'item_sub_categories.sub_not_found': {'message': 'Sub-category not found!', 'code': 'item_sub_categories.sub_not_found'},
        'item_sub_categories.name_taken': {'message': 'The name has already been taken.', 'code': 'item_sub_categories.name_taken'},
        'item_sub_categories.not_found': {'message': 'Item sub-category not found!', 'code': 'item_sub_categories.not_found'},
        # outlets endpoint
        'outlets.not_found': {'message': 'Outlet not found!', 'code': 'outlets.not_found'},
        # product dependant
        'products.no_variant_image_exist': {
            'message': 'The image variant must not be filled.',
            'code': 'products.no_variant_image_exist'
        },
        'products.len_image_variant': {
            'message': 'You must fill all variant images or even without images.',
            'code': 'products.len_image_variant'
        },
        'products.variant_not_found': {'message': 'Ticket variant not found!', 'code': 'products.variant_not_found'},
        'products.wholesale_not_found': {'message': 'Ticket wholesale not found!', 'code': 'products.wholesale_not_found'},
        'products.variant_product_id_not_found': {
            'message': 'You must fill an id on variant product.',
            'code': 'products.variant_product_id_not_found'
        },
        'products.image_product_delete.ext.not_allowed': {
            'message': 'Invalid image format on image_product_delete',
            'code': 'products.image_product_delete.ext.not_allowed'
        },
        'products.image_size_guide_delete.ext.not_allowed': {
            'message': 'Invalid image format on image_size_guide_delete',
            'code': 'products.image_size_guide_delete.ext.not_allowed'
        },
        # products endpoint
        'products.name_taken': {'message': 'The name has already been taken.', 'code': 'products.name_taken'},
        'products.item_sub_category_not_found': {'message': 'Item sub-category not found!', 'code': 'products.item_sub_category_not_found'},
        'products.brand_not_found': {'message': 'Brand not found!', 'code': 'products.brand_not_found'},
        'products.not_found': {'message': 'Product not found!', 'code': 'products.not_found'},
        'products.image_variant_not_found_in_db': {
            'message': 'The image on variant not found in db.',
            'code': 'products.image_variant_not_found_in_db'
        },
        'products.image_size_guide_delete_not_same_with_db': {
            'message': 'image_size_guide_delete not same with database.',
            'code': 'products.image_size_guide_delete_not_same_with_db'
        },
        'products.image_product_not_gt': {
            'message': 'Image is required, make sure this product has at least one image.',
            'code': 'products.image_product_not_gt'
        },
        'products.image_product_max_items': {'message': 'Maximal 10 images to be upload.', 'code': 'products.image_product_max_items'},
        # replies endpoint
        'replies.comment_not_found': {'message': 'Comment not found!', 'code': 'replies.comment_not_found'},
        'replies.cooldown': {
            'message': "You've already added comment a moment ago. Please try again later.",
            'code': 'replies.cooldown'
        },
        'replies.not_match': {'message': 'Reply not match with the current user.', 'code': 'replies.not_match'},
        'replies.not_found': {'message': 'Reply not found!', 'code': 'replies.not_found'},
        # shipping endpoint
        'shipping.failed_make_request': {'message': 'Failed to make a request to rajaongkir.', 'code': 'shipping.failed_make_request'}
    },
    'id': {
        # user controller
        'user_controller.not_admin': {'message': 'Hanya user dengan role admin yang dapat melakukan tindakan ini.','code': 'user_controller.not_admin'},
        'user_controller.not_found': {'message': 'User tidak ditemukan!', 'code': 'user_controller.not_found'},
        # magic image
        'single_image.not_lt': {'message': 'Gambar tidak boleh lebih dari {max_file_size} Mb.', 'code': 'single_image.not_lt', 'ctx': {}},
        'single_image.not_img': {'message': 'Tidak dapat mengidentifikasi gambar.', 'code': 'single_image.not_img'},
        'single_image.ext.not_allowed': {'message': 'Gambar harus di antara {extension}.', 'code': 'single_image.ext.not_allowed', 'ctx': {}},
        'multiple_image.ext.not_allowed': {
            'message': 'Gambar di indeks {index} harus di antara {extension}.',
            'code': 'multiple_image.ext.not_allowed',
            'ctx': {}
        },
        'multiple_image.not_img': {'message': 'Tidak dapat mengidentifikasi gambar pada indeks {index}.', 'code': 'multiple_image.not_img', 'ctx': {}},
        'multiple_image.not_lt': {
            'message': 'Gambar di indeks {index} tidak boleh lebih dari {max_file_size} Mb.',
            'code': 'multiple_image.not_lt',
            'ctx': {}
        },
        'multiple_image.not_unique': {'message': 'Setiap gambar harus unik.', 'code': 'multiple_image.not_unique'},
        'multiple_image.min_items': {'message': 'Setidaknya {min_file_in_list} gambar harus diupload.', 'code': 'multiple_image.min_items', 'ctx': {}},
        'multiple_image.max_items': {'message': 'Maksimal {max_file_in_list} gambar untuk diupload.', 'code': 'multiple_image.max_items', 'ctx': {}},
        # address endpoint
        'address.not_found': {'message': 'Alamat tidak ditemukan!', 'code': 'address.not_found'},
        'address.not_match': {'message': 'Alamat tidak sesuai dengan pengguna saat ini.', 'code': 'address.not_match'},
        # brands endpoint
        'brands.name_taken': {'message': 'Nama sudah dipakai.', 'code': 'brands.name_taken'},
        'brands.not_found': {'message': 'Brand tidak ditemukan!', 'code': 'brands.not_found'},
        # carts endpoint
        'carts.stock_not_enough_1': {'message': 'Jumlah yang Anda masukkan melebihi stok yang tersedia.', 'code': 'carts.stock_not_enough_1'},
        'carts.stock_not_enough_2': {
            'message': 'Item ini memiliki sisa stok {stock} dan Anda sudah memiliki {qty} di keranjang Anda.',
            'code': 'carts.stock_not_enough_2',
            'ctx': {}
        },
        'carts.max_items': {
            'message': 'Keranjang hanya dapat memuat 20 item. Hapus beberapa item untuk menambahkan yang lain.',
            'code': 'carts.max_items'
        },
        'carts.variant_not_found': {'message': 'Varian tidak ditemukan!', 'code': 'carts.variant_not_found'},
        # categories endpoint
        'categories.name_taken': {'message': 'Nama sudah dipakai.', 'code': 'categories.name_taken'},
        'categories.not_found': {'message': 'Kategori tidak ditemukan!', 'code': 'categories.not_found'},
        # comments endpoint
        'comments.is_admin': {'message': 'Admin tidak dapat membuat komentar di produk mereka sendiri.', 'code': 'comments.is_admin'},
        'comments.product_not_found': {'message': 'Produk tidak ditemukan!', 'code': 'comments.product_not_found'},
        'comments.cooldown': {
            'message': "Anda sudah menambahkan komentar beberapa saat yang lalu. Silakan coba lagi nanti.",
            'code': 'comments.cooldown'
        },
        'comments.not_match': {'message': 'Komentar tidak cocok dengan pengguna saat ini.', 'code': 'comments.not_match'},
        'comments.not_found': {'message': 'Komentar tidak ditemukan!', 'code': 'comments.not_found'},
        # discounts endpoint
        'discounts.product_not_found': {'message': 'Produk tidak ditemukan!', 'code': 'discounts.product_not_found'},
        'discounts.variant_not_found': {'message': 'Varian tiket tidak ditemukan!', 'code': 'discounts.variant_not_found'},
        'discounts.has_discount': {'message': 'Produk sudah ada diskon.', 'code': 'discounts.has_discount'},
        'discounts.variant_not_same': {'message': 'Varian tidak sama dengan produk.', 'code': 'discounts.variant_not_same'},
        'discounts.missing': {'message': 'Anda harus menetapkan diskon pada produk sebelum memperbaruinya.', 'code': 'discounts.missing'},
        'discounts.start_time': {'message': 'Waktu mulai baru harus setelah waktu mulai yang ditetapkan.', 'code': 'discounts.start_time'},
        'discounts.min_exp': {'message': 'Waktu kedaluwarsa setidaknya harus satu jam lebih lama dari waktu mulai.', 'code': 'discounts.min_exp'},
        'discounts.max_exp': {'message': 'Periode promo harus kurang dari 180 hari.', 'code': 'discounts.max_exp'},
        # item_sub_categories endpoint
        'item_sub_categories.sub_not_found': {'message': 'Sub-kategori tidak ditemukan!', 'code': 'item_sub_categories.sub_not_found'},
        'item_sub_categories.name_taken': {'message': 'Nama sudah dipakai.', 'code': 'item_sub_categories.name_taken'},
        'item_sub_categories.not_found': {'message': 'Item sub-kategori tidak ditemukan!', 'code': 'item_sub_categories.not_found'},
        # outlets endpoint
        'outlets.not_found': {'message': 'Outlet tidak ditemukan!', 'code': 'outlets.not_found'},
        # product dependant
        'products.no_variant_image_exist': {
            'message': 'Varian gambar tidak boleh diisi.',
            'code': 'products.no_variant_image_exist'
        },
        'products.len_image_variant': {
            'message': 'Anda harus mengisi semua gambar varian atau bahkan tanpa gambar.',
            'code': 'products.len_image_variant'
        },
        'products.variant_not_found': {'message': 'Varian tiket tidak ditemukan!', 'code': 'products.variant_not_found'},
        'products.wholesale_not_found': {'message': 'Grosir tiket tidak ditemukan!', 'code': 'products.wholesale_not_found'},
        'products.variant_product_id_not_found': {
            'message': 'Anda harus mengisi id pada varian produk.',
            'code': 'products.variant_product_id_not_found'
        },
        'products.image_product_delete.ext.not_allowed': {
            'message': 'Format gambar pada image_product_delete tidak valid',
            'code': 'products.image_product_delete.ext.not_allowed'
        },
        'products.image_size_guide_delete.ext.not_allowed': {
            'message': 'Format gambar pada image_size_guide_delete tidak valid',
            'code': 'products.image_size_guide_delete.ext.not_allowed'
        },
        # products endpoint
        'products.name_taken': {'message': 'Nama sudah dipakai.', 'code': 'products.name_taken'},
        'products.item_sub_category_not_found': {'message': 'Item sub-kategori tidak ditemukan!', 'code': 'products.item_sub_category_not_found'},
        'products.brand_not_found': {'message': 'Brand tidak ditemukan!', 'code': 'products.brand_not_found'},
        'products.not_found': {'message': 'Produk tidak ditemukan!', 'code': 'products.not_found'},
        'products.image_variant_not_found_in_db': {
            'message': 'Gambar pada varian tidak ditemukan dalam db.',
            'code': 'products.image_variant_not_found_in_db'
        },
        'products.image_size_guide_delete_not_same_with_db': {
            'message': 'image_size_guide_delete tidak sama dengan database.',
            'code': 'products.image_size_guide_delete_not_same_with_db'
        },
        'products.image_product_not_gt': {
            'message': 'Gambar diperlukan, pastikan produk ini memiliki setidaknya satu gambar.',
            'code': 'products.image_product_not_gt'
        },
        'products.image_product_max_items': {'message': 'Maksimal 10 gambar untuk diupload.', 'code': 'products.image_product_max_items'},
        # replies endpoint
        'replies.comment_not_found': {'message': 'Komentar tidak ditemukan!', 'code': 'replies.comment_not_found'},
        'replies.cooldown': {
            'message': "Anda sudah menambahkan komentar beberapa saat yang lalu. Silakan coba lagi nanti.",
            'code': 'replies.cooldown'
        },
        'replies.not_match': {'message': 'Balasan tidak cocok dengan pengguna saat ini.', 'code': 'replies.not_match'},
        'replies.not_found': {'message': 'Balasan tidak ditemukan!', 'code': 'replies.not_found'},
        # shipping endpoint
        'shipping.failed_make_request': {'message': 'Gagal melakukan request ke rajaongkir.', 'code': 'shipping.failed_make_request'}
    }
}
