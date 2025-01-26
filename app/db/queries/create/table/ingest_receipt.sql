CREATE TABLE IF NOT EXISTS finance.ingest.receipt (
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    photo VARCHAR(255) NOT NULL,
    store VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ,
    tax FLOAT NOT NULL,
    total FLOAT NOT NULL,
    item_code INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_quantity INT NOT NULL,
    item_price FLOAT NOT NULL,
    item_is_discount BOOLEAN NOT NULL,
    UNIQUE (photo,item_code)
);