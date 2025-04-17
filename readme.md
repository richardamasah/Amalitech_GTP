# 📦 Inventory Management System (SQL Project)
Final SQL project by **Sir Djanie**

---

## 🧾 Overview
This SQL project simulates a full inventory and order management system for an e-commerce business. It includes:

- Product and customer management
- Order placement with stock updates
- Inventory change logging
- Stock replenishment automation
- Reporting views and business summaries
- Customer spending categorization with discounts

---

## 📁 Folder Structure

| File Name           | Description |
|---------------------|-------------|
| `1_schema.sql`      | Contains all table creation scripts and relationships |
| `2_queries.sql`     | Contains stored procedures (order handling, discount, etc.) |
| `3_views.sql`       | Views for order summary, stock insights, and customer tiers |
| `4_replenishment.sql` | Procedure + event to handle daily stock restocking |
| `5_reports.sql`     | Sample queries for order summaries, low stock reports, top spenders, etc. |
| `sample_data.sql`   | Optional insert statements for testing the system |
| `full_project.sql`  | All-in-one complete SQL script with everything organized |
| `README.md`         | This file 😊 |

---

## 📌 Key Features

✅ Order placement with automatic:
- Stock deduction  
- Total calculation  
- Discount application  
- Inventory logging  

✅ Views for:
- Order summary  
- Low stock alerts  
- Customer tiering (Bronze/Silver/Gold)

✅ Stock replenishment:
- Fully automated daily restock via SQL event
- Optional trigger-based inventory logging

---

## 🧠 Reporting Queries
See `5_reports.sql` for:
- Orders per customer
- Products needing replenishment
- Top spending customers
- Product sales summary

---

## 🚀 Author
Built with SQL by **Sir Djanie**  
Inspired by real-world systems. Designed to impress and automate.

