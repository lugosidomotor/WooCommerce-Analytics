#!/bin/bash

docker stop woo-dump-mysql
docker rm -f woo-dump-mysql

for i in {5..0}; do echo $i; sleep 1; done; echo "Docker stop complete!"

# MySQL konténer indítása
docker run --name woo-dump-mysql -e MYSQL_ROOT_PASSWORD=admin -d -p 3306:3306 mysql:latest

for i in {30..0}; do echo $i; sleep 1; done; echo "Container start complete!"

# Adatbázis-dump másolása a konténerbe
docker cp dump.sql woo-dump-mysql:/dump.sql

# Adatbázis-dump importálása
docker exec -i woo-dump-mysql mysql -uroot -padmin <<< "CREATE DATABASE woo; USE woo; SOURCE /dump.sql;"

# Lekérdezés futtatása
docker exec -i woo-dump-mysql mysql -uroot -padmin woo <<< "SELECT * FROM wp_wc_order_stats;"

docker exec -i woo-dump-mysql mysql --default-character-set=utf8 -uroot -padmin woo <<< "WITH RECURSIVE CategoryChain AS (SELECT tt.term_id, tt.parent, t.name FROM wp_term_taxonomy AS tt INNER JOIN wp_terms AS t ON tt.term_id = t.term_id WHERE tt.taxonomy = 'product_cat' AND tt.parent = 0 UNION ALL SELECT tt.term_id, tt.parent, CONCAT(cc.name, ' > ', t.name) FROM wp_term_taxonomy AS tt INNER JOIN wp_terms AS t ON tt.term_id = t.term_id INNER JOIN CategoryChain AS cc ON tt.parent = cc.term_id WHERE tt.taxonomy = 'product_cat') SELECT * FROM CategoryChain;" > ./streamlit/categories.txt

docker exec -i woo-dump-mysql mysql -uroot -padmin --default-character-set=utf8 woo -e "SELECT os.order_id AS 'Order ID', os.date_created AS 'Date Created', os.total_sales AS 'Total Sales', pm1.meta_value AS 'Shipping Cost', pm2.meta_value AS 'Shipping Postcode', op.product_id AS 'Product ID', p.post_title AS 'Product Name', op.product_net_revenue AS 'Product Net Revenue', op.product_gross_revenue AS 'Product Gross Revenue', t.name AS 'Category Name' FROM wp_wc_order_stats os JOIN wp_wc_order_product_lookup op ON os.order_id = op.order_id JOIN wp_posts p ON op.product_id = p.ID JOIN wp_term_relationships tr ON p.ID = tr.object_id JOIN wp_term_taxonomy tt ON tr.term_taxonomy_id = tt.term_taxonomy_id JOIN wp_terms t ON tt.term_id = t.term_id LEFT JOIN wp_postmeta pm1 ON os.order_id = pm1.post_id AND pm1.meta_key = '_order_shipping' LEFT JOIN wp_postmeta pm2 ON os.order_id = pm2.post_id AND pm2.meta_key = '_shipping_postcode' WHERE p.post_type = 'product' AND tt.taxonomy = 'product_cat';" > ./streamlit/raw_sales.txt

cd ./streamlit
bash category_full_path.sh
docker build -t streamlit-app .

docker stop streamlit
docker rm -f streamlit
docker run -p 8501:8501 --name streamlit streamlit-app
