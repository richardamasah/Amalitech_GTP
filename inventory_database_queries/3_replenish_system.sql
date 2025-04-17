-- =============================================================================
--  PROCEDURE: ReplenishStock()
-- =============================================================================
--     Automatically finds all products where stock_quantity < reorder_level.
--     Replenishes stock by adding 50 units.
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
END;
//


-- =============================================================================
--  EVENT: auto_replenish
-- =============================================================================
--     Automates the ReplenishStock() procedure by running it every day.
--     Ensures stock is checked and replenished without manual intervention.
--     This is what makes the system self-managing — full automation of restocking.
-- =============================================================================

-- Make sure the event scheduler is turned on
SET GLOBAL event_scheduler = ON;


-- Create the event that runs daily
CREATE EVENT auto_replenish
ON SCHEDULE EVERY 1 DAY
DO
  CALL ReplenishStock();