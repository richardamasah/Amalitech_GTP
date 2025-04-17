-- =============================================================================
-- 📄 VIEW: order_summary_view
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