#!/bin/bash

# File paths
categories_file="./categories.txt"
sales_file="./raw_sales.txt"
output_file="./sales.txt"

# Create an associative array for full category paths
declare -A category_paths
while IFS=$'\t' read -r id parent name
do
    # Extract the last part of the category path (the category name)
    simple_name=$(echo $name | awk -F' > ' '{print $NF}')
    category_paths[$simple_name]=$name
done < <(tail -n +2 "$categories_file")

# Update the sales.txt file with new category paths
while IFS=$'\t' read -r order_id date_created email_hash total_sales shipping_cost shipping_postcode product_id product_name net_revenue gross_revenue category_name
do
    if [[ -n "${category_paths[$category_name]}" ]]; then
        updated_category="${category_paths[$category_name]}"
    else
        updated_category="$category_name"
    fi
    # Output the line with updated category name, leaving the email hash untouched
    echo -e "$order_id\t$date_created\t$email_hash\t$total_sales\t$shipping_cost\t$shipping_postcode\t$product_id\t$product_name\t$net_revenue\t$gross_revenue\t$updated_category"
done < "$sales_file" > "$output_file"

echo "Updated data can be found in the '$output_file' file."
