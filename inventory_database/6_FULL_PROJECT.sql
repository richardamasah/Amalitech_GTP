-- ============================================================
-- INVENTORY MANAGEMENT SYSTEM 
-- Author: Richard Amasah Djanie
-- ============================================================


-- ============================================================
-- 1. DATABASE SCHEMA: TABLE CREATION WITH RELATIONSHIPS
-- ============================================================

-- CREATE DATABASE
CREATE DATABASE Myinventory;
USE Myinventory;

-- CREATE PRODUCT TABLE
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    reorder_level INT DEFAULT 0
);

-- CUSTOMERS TABLE
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20)
);

-- ORDERS TABLE
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- ORDER DETAILS TABLE
CREATE TABLE order_details (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- INVENTORY LOGS TABLE
CREATE TABLE inventory_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    change_amount INT,
    change_type VARCHAR(50),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id));



    -- ============================================================
-- 2. STORED PROCEDURES: ORDER PLACEMENT & STOCK UPDATE
-- ============================================================

-- Procedure: place_order
-- Description:
--    Places an order.
--    Inserts into orders and order_details tables.
--    Deducts stock and logs inventory changes.
--    Calculates total amount of products ordered
-- ============================================
DELIMITER $$
CREATE PROCEDURE place_order(
    IN p_customer_id INT,         -- Customer placing the order
    IN p_product_id INT,          -- Product being ordered
    IN p_quantity INT             -- Quantity being ordered
)
BEGIN
    -- Declare local variables
    DECLARE v_order_id INT;
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_total DECIMAL(10,2);

    -- Step 1: Get product price
    
    SELECT price INTO v_price
    FROM products
    WHERE product_id = p_product_id;

    -- Step 2: Insert into orders table (new order)
    
    INSERT INTO orders (customer_id, order_date, total_amount)
    VALUES (p_customer_id, NOW(), 0.00);

    -- Get the new order ID
    SET v_order_id = LAST_INSERT_ID();

    
    -- Step 3: Insert into order_details table
    
    INSERT INTO order_details (order_id, product_id, quantity, price)
    VALUES (v_order_id, p_product_id, p_quantity, v_price);

    
    -- Step 4: Update product stock
   
    UPDATE products
    SET stock_quantity = stock_quantity - p_quantity
    WHERE product_id = p_product_id;



    -- Step 5: Calculate and update total
   
    SET v_total = v_price * p_quantity;

    UPDATE orders
    SET total_amount = v_total
    WHERE order_id = v_order_id;
END $$

DELIMITER ;


-- ============================================================
-- 2. -- Trigger to log stock changes in inventory_logs after updating the products table
       -- I created this trigger to show how a trigger works and logs information after 
       -- and update is made 
       -- But my place order procedure automatically logs the data. 
       -- Answeres question 2ii
-- ============================================================
DELIMITER $$
CREATE TRIGGER log_inventory_change
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    -- Log the difference in stock quantity (NEW - OLD) with 'AUTO-LOG' change type
    INSERT INTO inventory_logs (product_id, change_amount, change_type)
    VALUES (
        NEW.product_id,
        NEW.stock_quantity - OLD.stock_quantity,
        'stock update');
END $$

DELIMITER ;



DELIMITER $$
-- Phase 3: Monitoring and Reporting
-- QUESTION 3

-- =============================================================================
--  PROCEDURE TO PLACE ORDER WITH DISCOUNT
-- =============================================================================
--     This procedure handles the following.
--     - Placing orders
--     - Deducting stock
--     - Logging inventory changes
--     - Applying bulk discounts
--     - Calculating total amount
-- =============================================================================

CREATE PROCEDURE place_order_full(
    IN p_customer_id INT,      -- Customer placing the order
    IN p_product_id INT,       -- Product ID being ordered
    IN p_quantity INT          -- Quantity of the product ordered
)
BEGIN
    -- ============================
    -- Step 1: Declare variables
    -- ============================
    DECLARE v_order_id INT;
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_total DECIMAL(10,2);
    DECLARE v_discount_rate DECIMAL(5,2);
    DECLARE v_final_total DECIMAL(10,2);

    -- ============================
    -- Step 2: Get product price
    -- ============================
    SELECT price INTO v_price
    FROM products
    WHERE product_id = p_product_id;

    -- ============================
    -- Step 3: Insert order (initial total = 0)
    -- ============================
    INSERT INTO orders (customer_id, order_date, total_amount)
    VALUES (p_customer_id, NOW(), 0.00);

    -- Get the new order ID
    SET v_order_id = LAST_INSERT_ID();

    -- ============================
    -- Step 4: Add product to order_details
    -- ============================
    INSERT INTO order_details (order_id, product_id, quantity, price)
    VALUES (v_order_id, p_product_id, p_quantity, v_price);

    -- ============================
    -- Step 5: Deduct product stock
    -- ============================
    UPDATE products
    SET stock_quantity = stock_quantity - p_quantity
    WHERE product_id = p_product_id;

    -- ============================
    -- Step 6: Log inventory change
    -- ============================
    INSERT INTO inventory_logs (product_id, change_amount, change_type)
    VALUES (p_product_id, -p_quantity, 'ORDER');

    -- ============================
    -- Step 7: Apply bulk discount logic
    --     10+ items = 10% discount
    --     5-9 items = 5% discount
    --     <5 = no discount
    -- ============================
    SET v_discount_rate = CASE
        WHEN p_quantity >= 10 THEN 0.10
        WHEN p_quantity >= 5 THEN 0.05
        ELSE 0.00
    END;

    -- ============================
    -- Step 8: Calculate total & final amount
    -- ============================
    SET v_total = v_price * p_quantity;
    SET v_final_total = v_total - (v_total * v_discount_rate);

    -- ============================
    -- Step 9: Update final amount in orders table
    -- ============================
    UPDATE orders
    SET total_amount = v_final_total
    WHERE order_id = v_order_id;
END $$

DELIMITER ;



 -- QUESTION 3 ii
-- =============================================================================
--   CUSTOMER SPENDING CATEGORY
-- =============================================================================
--     Shows total spending of each customer and assigns them to a loyalty tier.
--     - Bronze: < 500
--     - Silver: 500 - 999
--     - Gold: 1000+
-- =============================================================================

CREATE VIEW customer_spending_category AS
SELECT 
    c.customer_id,
    c.name AS customer_name,
    SUM(o.total_amount) AS total_spent,
    CASE 
        WHEN SUM(o.total_amount) >= 1000 THEN 'Gold'
        WHEN SUM(o.total_amount) >= 500 THEN 'Silver'
        ELSE 'Bronze'
    END AS customer_tier
FROM 
    customers c
JOIN 
    orders o ON c.customer_id = o.customer_id
GROUP BY 
    c.customer_id, c.name;




-- Phase 4: Stock Replenishment and Automation

-- =============================================================================
--  PROCEDURE: ReplenishStock()
-- =============================================================================
--     Automatically finds all products where stock_quantity < reorder_level.
--     Replenishes stock by adding 20 units.
--     Logs each replenishment into inventory_logs.

-- =============================================================================

DELIMITER //

CREATE PROCEDURE ReplenishStock()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE prod_id INT;
    DECLARE qty_to_add INT DEFAULT 20;

    -- Cursor to get all products that need restocking
    DECLARE stock_cursor CURSOR FOR
        SELECT product_id FROM products WHERE stock_quantity < reorder_level;

    -- Handler for end of cursor loop
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Open the cursor
    OPEN stock_cursor;

    -- Loop through low stock products and update stock
    replenish_loop: LOOP
        FETCH stock_cursor INTO prod_id;
        IF done THEN
            LEAVE replenish_loop;
        END IF;

        -- Add stock to the product
        UPDATE products
        SET stock_quantity = stock_quantity + qty_to_add
        WHERE product_id = prod_id;

        -- Log the restock 
        INSERT INTO inventory_logs (product_id, change_amount, change_type)
        VALUES (prod_id, qty_to_add, 'RESTOCK');
    END LOOP;

    -- Close the cursor
    CLOSE stock_cursor;
END //

DELIMITER ;




-- =============================================================================
--  EVENT: auto_replenish
-- =============================================================================
--     Automates the ReplenishStock() procedure by running it every day.
--     Ensures stock is checked and replenished without manual intervention.
--     This is what makes the system self-managing — full automation of restocking.
-- =============================================================================

-- Turn scheduler On to run daily
SET GLOBAL event_scheduler = ON;


-- Create the event that runs daily
CREATE EVENT auto_replenish
ON SCHEDULE EVERY 1 DAY
DO
  CALL ReplenishStock();



-- question 5
-- Phase 5: Advanced Queries

  -- =============================================================================
--  VIEW: order_summary_view
-- =============================================================================
--     This view displays a summary of all customer orders, showing:
--     - Customer name
--     - Order ID and date
--     - Total order amount
--     - Total number of items in the order
-- =============================================================================

CREATE VIEW order_summary_view AS
SELECT 
    o.order_id,                                 -- Unique order ID
    c.name AS customer_name,                    -- Customer's name
    o.order_date,                               -- Date order was placed
    o.total_amount,                             -- Total amount for the order
    SUM(od.quantity) AS total_items             -- Total items across products in the order
FROM 
    orders o
JOIN 
    customers c ON o.customer_id = c.customer_id    -- Link order to customer
JOIN 
    order_details od ON o.order_id = od.order_id    -- Link order to its items
GROUP BY 
    o.order_id, c.name, o.order_date, o.total_amount;




    -- =============================================================================
--   VIEW TO CHECK STOCK INTO TO DETERMINE LOW STOCK IN DATABASE
-- =============================================================================
--     This view identifies all products that are low on stock.
--     It shows:
--     - Product ID, name, category
--     - Current stock quantity
--     - Reorder threshold level
--
-- =============================================================================

CREATE VIEW low_stock_view AS
SELECT 
    product_id,           -- Product ID
    name,                 -- Product name
    category,             -- Product category
    stock_quantity,       -- Current quantity in stock
    reorder_level         -- Threshold to trigger replenishment
FROM 
    products
WHERE 
    stock_quantity < reorder_level;   -- Only show products below the reorder level