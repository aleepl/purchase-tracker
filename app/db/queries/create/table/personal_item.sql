CREATE TABLE IF NOT EXISTS finance.personal.item (
    id INT NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    code INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    receipt_id INT NOT NULL REFERENCES finance.personal.receipt(id),
    UNIQUE (receipt_id,code)
);