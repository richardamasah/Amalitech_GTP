SELECT * 
FROM order_summary_view
WHERE customer_name = 'John Doe';

SELECT * 
FROM low_stock_view;

SELECT * 
FROM customer_spending_summary;



SELECT *
FROM customer_spending_category;


-- Quantity sold per product
SELECT 
    p.name,
    SUM(od.quantity) AS total_sold
FROM 
    order_details od
JOIN 
    products p ON od.product_id = p.product_id
GROUP BY 
    p.product_id, p.name
ORDER BY 
    total_sold DESC;

    CALL ReplenishStock();