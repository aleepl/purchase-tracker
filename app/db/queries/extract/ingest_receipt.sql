SELECT
    id,
    photo,
    store,
    address,
    timestamp,
    tax,
    total,
    item_code,
    item_name,
    item_quantity,
    item_price,
    item_is_discount
FROM finance.ingest.receipt;