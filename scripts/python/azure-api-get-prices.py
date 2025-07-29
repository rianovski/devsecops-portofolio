import requests
import psycopg2

# Function to fetch data from the URL
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('Items', [])
        next_page_link = data.get('NextPageLink')
        return items, next_page_link
    else:
        print(f"Failed to fetch data from URL: {url}")
        return [], None

# Function to create table in PostgreSQL
def create_table():
    try:
        connection = psycopg2.connect(
            dbname="devsecops",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS azure_pricing (
            id SERIAL PRIMARY KEY,
            currency_code VARCHAR(10),
            tier_minimum_units FLOAT,
            retail_price FLOAT,
            unit_price FLOAT,
            arm_region_name VARCHAR(50),
            location VARCHAR(50),
            effective_start_date TIMESTAMP,
            meter_id VARCHAR(50),
            meter_name VARCHAR(100),
            product_id VARCHAR(50),
            sku_id VARCHAR(50),
            product_name VARCHAR(255),
            sku_name VARCHAR(255),
            service_name VARCHAR(100),
            service_id VARCHAR(50),
            service_family VARCHAR(100),
            unit_of_measure VARCHAR(50),
            type VARCHAR(50),
            is_primary_meter_region BOOLEAN,
            arm_sku_name VARCHAR(100)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully.")
    except psycopg2.Error as error:
        print("Error:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

# Function to connect to PostgreSQL and insert/update data
def insert_data(data):
    try:
        connection = psycopg2.connect(
            dbname="devsecops",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        total_inserted = 0

        for item in data:
            # Check if meter_id exists in the database
            cursor.execute("SELECT meter_id FROM azure_pricing WHERE meter_id = %s", (item.get('meterId'),))
            existing_meter = cursor.fetchone()

            if existing_meter:
                # Update the existing record
                cursor.execute("""
                    UPDATE azure_pricing SET
                    currency_code = %s,
                    tier_minimum_units = %s,
                    retail_price = %s,
                    unit_price = %s,
                    arm_region_name = %s,
                    location = %s,
                    effective_start_date = %s,
                    meter_name = %s,
                    product_id = %s,
                    sku_id = %s,
                    product_name = %s,
                    sku_name = %s,
                    service_name = %s,
                    service_id = %s,
                    service_family = %s,
                    unit_of_measure = %s,
                    type = %s,
                    is_primary_meter_region = %s,
                    arm_sku_name = %s
                    WHERE meter_id = %s
                """, (
                    item.get('currencyCode'), item.get('tierMinimumUnits'), 
                    item.get('retailPrice'), item.get('unitPrice'), 
                    item.get('armRegionName'), item.get('location'), 
                    item.get('effectiveStartDate'), item.get('meterName'), 
                    item.get('productId'), item.get('skuId'), 
                    item.get('productName'), item.get('skuName'), 
                    item.get('serviceName'), item.get('serviceId'), 
                    item.get('serviceFamily'), item.get('unitOfMeasure'), 
                    item.get('type'), item.get('isPrimaryMeterRegion'), 
                    item.get('armSkuName'), item.get('meterId')
                ))
            else:
                # Insert a new record
                cursor.execute("""
                    INSERT INTO azure_pricing VALUES (
                        DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    item.get('currencyCode'), item.get('tierMinimumUnits'), 
                    item.get('retailPrice'), item.get('unitPrice'), 
                    item.get('armRegionName'), item.get('location'), 
                    item.get('effectiveStartDate'), item.get('meterId'), 
                    item.get('meterName'), item.get('productId'), 
                    item.get('skuId'), item.get('productName'), 
                    item.get('skuName'), item.get('serviceName'), 
                    item.get('serviceId'), item.get('serviceFamily'), 
                    item.get('unitOfMeasure'), item.get('type'), 
                    item.get('isPrimaryMeterRegion'), item.get('armSkuName')
                ))
                total_inserted += 1

        connection.commit()
        print(f"Data inserted successfully. Total inserted: {total_inserted}")
        return total_inserted
    except psycopg2.Error as error:
        print("Error:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

# Main function to orchestrate the process
def main():
    create_table()
    url = "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&$filter=location eq 'AP Southeast' and serviceName eq 'Virtual Machines'"
    total_items_processed = 0
    total_items_inserted = 0
    while url:
        page_count = 0
        print("Fetching data from page...")
        data, url = fetch_data(url)
        if data:
            page_count += 1
            total_items_processed += len(data)
            print(f"Page {page_count}: Fetched {len(data)} items.")
            total_items_inserted += insert_data(data)
            print(f"Total items processed: {total_items_processed}, Total items inserted: {total_items_inserted}")

if __name__ == "__main__":
    main()
