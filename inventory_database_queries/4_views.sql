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