import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Connect to the MySQL database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ecommerce_system',
            user='root',
            password='honey4kush@#'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

############################# Function to execute table creation queries ##########################
def create_tables(cursor):
    queries = [
        '''CREATE TABLE IF NOT EXISTS Customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        );''',
        '''CREATE TABLE IF NOT EXISTS Products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock INT NOT NULL
        );''',
        '''CREATE TABLE IF NOT EXISTS Orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            order_date DATE NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        );''',
        '''CREATE TABLE IF NOT EXISTS OrderDetails (
            order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            product_id INT,
            quantity INT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders(order_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        );''',
        '''CREATE TABLE IF NOT EXISTS Payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            amount DECIMAL(10, 2) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        );'''
    ]

    ################ Execute each query ###############
    for query in queries:
        cursor.execute(query)

########### Connect to MySQL ###############
connection = create_connection()
if connection:
    cursor = connection.cursor()
    create_tables(cursor)
    connection.commit()
    cursor.close()
    connection.close()

############################### class_user #########################
    
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save(self, cursor, connection):
        cursor.execute("INSERT INTO Customers (name, email) VALUES (%s,%s)", (self.name,self.email))
        connection.commit()

    @staticmethod
    def get_customer(cursor, customer_id):
        cursor.execute("SELECT * FROM Customers WHERE customer_id = %s", (customer_id,))
        return cursor.fetchone()


class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def save(self, cursor, connection):
        cursor.execute("INSERT INTO Products (name, price, stock) VALUES (%s, %s, %s)", (self.name, self.price, self.stock))
        connection.commit()

    @staticmethod
    def get_product(cursor, product_id):
        cursor.execute("SELECT * FROM Products WHERE product_id = %s", (product_id,))
        return cursor.fetchone()


class Order:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.order_date = datetime.now().strftime('%Y-%m-%d')
        self.status = "pending"

    def create_order(self, cursor, connection):
        cursor.execute("INSERT INTO Orders (customer_id, order_date, status) VALUES (%s, %s, %s)", 
                       (self.customer_id, self.order_date, self.status))
        connection.commit()
        return cursor.lastrowid

    @staticmethod
    def add_product_to_order(cursor, connection, order_id, product_id, quantity):
        cursor.execute("INSERT INTO OrderDetails (order_id, product_id, quantity) VALUES (%s, %s, %s)", 
                       (order_id, product_id, quantity))
        connection.commit()


class Payment:
    def __init__(self, order_id, amount):
        self.order_id = order_id
        self.amount = amount
        self.status = "pending"

    def make_payment(self, cursor, connection):
        cursor.execute("INSERT INTO Payments (order_id, amount, status) VALUES (%s, %s, %s)", 
                       (self.order_id, self.amount, self.status))
        connection.commit()

    def complete_payment(self, cursor, connection):
        cursor.execute("UPDATE Payments SET status = 'completed' WHERE order_id = %s", (self.order_id,))
        connection.commit()


#############################                 #############################

def process_orders(orders, cursor, connection):
    for order in orders:
        for product_id, quantity in order.items():
            product = Product.get_product(cursor, product_id)
            if product[3] >= quantity:
                new_stock = product[3] - quantity
                cursor.execute("UPDATE Products SET stock = %s WHERE product_id = %s", (new_stock, product_id))
                connection.commit()

                if new_stock < 10:  # Threshold
                    print(f"Alert: Product {product[1]} needs restocking!")
            else:
                print(f"Error: Not enough stock for {product[1]}")

def restock_items(restock_list, cursor, connection):
    for product_id, quantity in restock_list.items():
        product = Product.get_product(cursor, product_id)
        new_stock = product[3] + quantity
        cursor.execute("UPDATE Products SET stock = %s WHERE product_id = %s", (new_stock, product_id))
        connection.commit()


####################### main connection ##############################################

def insert_data(cursor, connection):
   
    users = [
        User('John Doe', 'john@example.com'),
        User('Jane Smith', 'jane@example.com'),
        User('Alice Johnson', 'alice@example.com')
    ]
    for user in users:
        user.save(cursor, connection)
    
    #################### Insert multiple products ##################
    products = [
        Product('Laptop', 1200.99, 50),
        Product('Phone', 799.99, 100),
        Product('Headphones', 199.99, 200)
    ]
    for product in products:
        product.save(cursor, connection)

    # Insert orders and payments
    for user in users:
        cursor.execute("SELECT customer_id FROM Customers WHERE email = %s", (user.email,))
        customer_id = cursor.fetchone()[0]

        order = Order(customer_id)
        order_id = order.create_order(cursor, connection)

        # Add products to the order (for simplicity, adding product_id 1 and 2)
        Order.add_product_to_order(cursor, connection, order_id, 1, 2)  # Add 2 Laptops
        Order.add_product_to_order(cursor, connection, order_id, 2, 1)  # Add 1 Phone

        # Insert payment for the order
        payment = Payment(order_id, 2000.00)  # Example amount
        payment.make_payment(cursor, connection)
        payment.complete_payment(cursor, connection)

connection = create_connection()
if connection:
    cursor = connection.cursor()
    create_tables(cursor)
    insert_data(cursor, connection)
    connection.commit()
    cursor.close()
    connection.close()




