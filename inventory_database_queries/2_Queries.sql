-- ============================================================
-- 2. STORED PROCEDURES: ORDER PLACEMENT & STOCK UPDATE
-- ============================================================

-- Procedure: place_order
-- Description:
--    Places an order.
--    Inserts into orders and order_details tables.
--    Deducts stock and logs inventory changes.
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


    -- =================================
    -- Step 5: Calculate and update total
    -- =================================
    SET v_total = v_price * p_quantity;

    UPDATE orders
    SET total_amount = v_total
    WHERE order_id = v_order_id;
END $$



-- ============================================================
-- 2. -- Trigger to log stock changes in inventory_logs after updating the products table
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




-- Phase 3: Monitoring and Reporting

DELIMITER $$

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


-- =============================================================================
--   CUSTOMER SPENDING SUMMARY
-- =============================================================================
--     Shows total spending of each customer and assigns them to a loyalty tier.
--     - Bronze: < 500
--     - Silver: 500 - 999
--     - Gold: 1000+
-- =============================================================================

CREATE VIEW customer_spending_summary AS
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