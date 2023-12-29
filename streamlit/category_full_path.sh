#!/bin/bash

# Fájl elérési utak
categories_file="./categories.txt"
sales_file="./sales.txt"
output_file="./eladasok.txt"

# Létrehoz egy asszociatív tömböt a kategóriák teljes útjával
declare -A category_paths
while IFS=$'\t' read -r id parent name
do
    # Az utolsó '>' utáni rész (a kategória neve) kinyerése
    simple_name=$(echo $name | awk -F' > ' '{print $NF}')
    category_paths[$simple_name]=$name
done < <(tail -n +2 "$categories_file")

# Frissíti a sales.txt fájlt az új kategória-útvonalakkal
while IFS=$'\t' read -r order_id date_created total_sales shipping_cost shipping_postcode product_id product_name net_revenue gross_revenue category_name
do
    if [[ -n "${category_paths[$category_name]}" ]]; then
        updated_category="${category_paths[$category_name]}"
    else
        updated_category="$category_name"
    fi
    echo -e "$order_id\t$date_created\t$total_sales\t$shipping_cost\t$shipping_postcode\t$product_id\t$product_name\t$net_revenue\t$gross_revenue\t$updated_category"
done < "$sales_file" > "$output_file"

echo "A frissített adatokat a '$output_file' fájlban találod."
