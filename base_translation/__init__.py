
def overwrite_us_translation(oslo):
    """
    Hint to overwrite translation using rpc
    Args:
        oslo: rpc (oerplib)
    """
    search_ctx = oslo.context.copy()
    search_ctx['active_test'] = False

    product_ids = oslo.get('product.product').search([], context=search_ctx)
    done_ids = []

    us_read_ctx = oslo.context.copy()
    us_read_ctx['lang'] = 'en_US'

    def print_progress():
        print(len(done_ids), '/', len(product_ids))

    fields = ['name', 'description', 'description_sale', 'description_purchase']
    count = 0
    for id in product_ids:
        if not id in done_ids:
            us_vals = oslo.get('product.product').read(
                fields, context=us_read_ctx
            )
            fr_vals = oslo.get('product.product').read(id, fields)
            if not fr_vals == us_vals:
                print('us_vals', us_vals)
                print('fr_vals', fr_vals)
                diff_vals = dict(set(fr_vals.items()) - set(us_vals.items()))
                print('##_vals', diff_vals)
                oslo.get('product.product').write(fr_vals.pop('id'), diff_vals)
            done_ids.append(id)
            count += 1
        if len(done_ids) % 100 == 0:
            print_progress()

    print_progress()
