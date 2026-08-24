
USE classicmodels;
  
DROP TABLE IF EXISTS dim_dates;
 
CREATE TABLE dim_dates AS
WITH RECURSIVE date_seq AS (
    SELECT DATE('2003-01-01') AS full_date
    UNION ALL
    SELECT full_date + INTERVAL 1 DAY
    FROM date_seq
    WHERE full_date < '2005-12-31'
)
SELECT
    full_date            AS date_key,
    YEAR(full_date)       AS year,
    QUARTER(full_date)    AS quarter,
    MONTH(full_date)      AS month,
    MONTHNAME(full_date)  AS month_name,
    DAY(full_date)        AS day,
    DAYNAME(full_date)    AS day_name,
    WEEK(full_date, 1)    AS week
FROM date_seq;
 
ALTER TABLE dim_dates ADD PRIMARY KEY (date_key);
 
-- ============================================================
-- 2. DIMENSION : dim_offices (Bureaux)
-- ============================================================
 
CREATE OR REPLACE VIEW dim_offices AS
SELECT
    officeCode,
    city,
    phone,
    country,
    territory
FROM offices;
 
-- ============================================================
-- 3. DIMENSION : dim_customers (Clients)
-- ============================================================
 
CREATE OR REPLACE VIEW dim_customers AS
SELECT
    customerNumber,
    customerName,
    contactLastName,
    contactFirstName,
    city,
    state,
    postalCode,
    country,
    salesRepEmployeeNumber
FROM customers;
 
-- ============================================================
-- 4. DIMENSION : dim_products (Produits)
-- ============================================================
 
CREATE OR REPLACE VIEW dim_products AS
SELECT
    productCode,
    productName,
    productLine,
    productScale,
    productVendor,
    buyPrice
FROM products;
 
-- ============================================================
-- 5. DIMENSION : dim_employees (Employes & RH)
 
CREATE OR REPLACE VIEW dim_employees AS
SELECT
    e.employeeNumber,
    e.lastName,
    e.firstName,
    e.jobTitle,
    e.officeCode,
    o.city    AS officeCity,
    o.country AS officeCountry,
    e.reportsTo
FROM employees e
JOIN offices o ON e.officeCode = o.officeCode;
 
-- ============================================================
-- 6. FAIT : fact_sales (Ventes)
-- ============================================================
 
CREATE OR REPLACE VIEW fact_sales AS
SELECT
    o.orderNumber,
    od.productCode,
    o.customerNumber,
    c.salesRepEmployeeNumber,
    o.orderDate,
    od.quantityOrdered,
    od.priceEach,
    (od.quantityOrdered * od.priceEach)                AS totalRevenue,
    ((od.priceEach - p.buyPrice) * od.quantityOrdered)  AS margin,
    o.status AS orderStatus
FROM orders o
JOIN orderdetails od ON o.orderNumber = od.orderNumber
JOIN products p      ON od.productCode = p.productCode
JOIN customers c      ON o.customerNumber = c.customerNumber;
 
-- ============================================================
-- 7. FAIT : fact_payments (Paiements)
-- ============================================================
 
CREATE OR REPLACE VIEW fact_payments AS
SELECT
    checkNumber,
    customerNumber,
    paymentDate,
    amount
FROM payments;
 
-- ============================================================
-- 8. FAIT : fact_inventory (Logistique & Stocks)
 
CREATE OR REPLACE VIEW fact_inventory AS
SELECT
    p.productCode,
    p.quantityInStock,
    CAST(SUM(od.quantityOrdered) OVER (
        PARTITION BY p.productCode
        ORDER BY o.orderDate, o.orderNumber
    ) AS UNSIGNED)                            AS totalQuantitySold,
    DATEDIFF(o.shippedDate, o.orderDate)       AS deliveryDelayDays,
    IF(o.shippedDate > o.requiredDate, 1, 0)   AS isLate
FROM products p
JOIN orderdetails od ON p.productCode = od.productCode
JOIN orders o         ON od.orderNumber = o.orderNumber;
 
-- ============================================================
-- 9. VERIFICATIONS RAPIDES
-- ============================================================
 
SELECT * FROM dim_customers  LIMIT 10;
SELECT * FROM dim_products   LIMIT 10;
SELECT * FROM dim_employees  LIMIT 10;
SELECT * FROM dim_offices    LIMIT 10;
SELECT * FROM dim_dates      LIMIT 10;
SELECT * FROM fact_sales     LIMIT 10;
SELECT * FROM fact_payments  LIMIT 10;
SELECT * FROM fact_inventory LIMIT 10;
 