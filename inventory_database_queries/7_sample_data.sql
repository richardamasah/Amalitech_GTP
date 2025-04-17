INSERT INTO products (name, category, price, stock_quantity, reorder_level) VALUES
('Wireless Mouse', 'Electronics', 15.99, 20, 5),
('USB-C Charger', 'Electronics', 22.50, 10, 3),
('Notebook', 'Stationery', 2.99, 50, 10),
('Desk Lamp', 'Furniture', 18.75, 5, 2),
('Water Bottle', 'Accessories', 9.99, 8, 4);

INSERT INTO customers (name, email, phone) VALUES
('Alice Johnson', 'alice@example.com', '0712345678'),
('Brian Smith', 'brian@example.com', '0722233344'),
('Carol Njeri', 'carol@example.com', '0733555666'),
('David Mwangi', 'david@example.com', '0744777888'),
('Eve Mutiso', 'eve@example.com', '0755999000');


-- Assume customers 1 and 2 made orders
INSERT INTO orders (customer_id, total_amount) VALUES
(1, 31.98),  -- 2x Wireless Mouse
(2, 25.49);  -- 1x Desk Lamp + 1x Water Bottle


-- ============================
-- INSERT INTO ORDER_DETAILS TABLE
-- ============================
-- Order 1: 2x Wireless Mouse at 15.99 each
INSERT INTO order_details (order_id, product_id, quantity, price) VALUES
(1, 1, 2, 15.99),
(2, 4, 1, 18.75),
(2, 5, 1, 6.74);  -- Discounted or changed price (for variety)