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


    -- ============================
    -- Step 5: Calculate and update total
    -- ============================
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