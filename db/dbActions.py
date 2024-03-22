import sqlite3
import logging

client_id = 'ShopBot'
product_table_name = 'products'
category_table_name = 'categories'


class Logger:
    def __init__(self, filename=None):
        logging.basicConfig(format='%(asctime)s %(message)s',
                            datefmt='%m.%d.%Y %I:%M:%S %p',
                            level=logging.INFO, filename=filename)

    def print_log(self, msg):
        logging.info(msg)


class DB:
    def __init__(self, db_name, log_handler):
        self.db_name = db_name
        self.logit = log_handler
        self.logit.print_log('Connecting to db...')

        self.con = sqlite3.connect(db_name)
        self.create_table()
        self.logit.print_log('Successful db connection')

    def connection(self):
        self.con = sqlite3.connect(self.db_name)
        return self.con

    def close(self):
        self.con.close()

    def create_table(self):
        try:
            con = self.connection()
            cur = con.cursor()
            sql = "create table if not exists products" \
                  "(" \
                  "productID     integer primary key autoincrement not NULL ," \
                  "productTitle  varchar(150)," \
                  "productPrice  integer," \
                  "productCount  integer," \
                  "productFile   varchar(150)," \
                  "categoryTitle varchar(150)" \
                  "references categories" \
                  ");"
            cur.execute(sql)
            cur.close()
            con.commit()
        except Exception as e:
            self.logit.print_log(e)

    def add_product(self, title, price, count, category, filename):
        con = self.connection()
        cur = con.cursor()
        cur.execute(
            f"INSERT INTO products(productTitle, productPrice, productCount, productFile, categoryTitle)"
            f" VALUES ('{title}', {price}, {count}, '{filename}', '{category}')")
        self.con.commit()
        con.close()

    def delete_product(self, id):
        con = self.connection()
        cur = con.cursor()
        cur.execute(f"DELETE FROM {product_table_name} WHERE productID={id}")
        self.con.commit()
        con.close()

    def update_product(self, id, title=None, price=None, count=None, category=None, filename=None):
        con = self.connection()
        cur = con.cursor()
        sql = ''
        if title:
            sql += f'productTitle="{title.rstrip()}",'

        if price:
            sql += f'productPrice={price},'

        if count:
            sql += f'productCount={count},'

        if filename:
            sql += f'productFile="{filename}",'

        if category:
            sql += f'categoryTitle="{category.rstrip()}",'

        sql = sql.rstrip(',')
        if sql[0] == ',':
            sql = sql[1:] + ' '
        if sql:
            cur.execute(f"UPDATE {product_table_name} SET {sql} "
                        f" WHERE productID={id};")


        con.commit()
        con.close()

    def get_product(self, id):
        con = self.connection()
        cur = con.cursor()
        product = cur.execute(f'SELECT * FROM {product_table_name} WHERE productID={id}').fetchone()
        product = {'id': product[0], 'title': product[1],
                   'price': product[2], 'count': product[3], 'file': product[4], 'category': product[5]}

        con.close()
        return product

    def get_products(self):
        con = self.connection()
        cur = con.cursor()
        products = cur.execute(f'SELECT * FROM {product_table_name}').fetchall()
        products = [{'id': el[0], 'title': el[1], 'price': el[2],
                     'count': el[3], 'file': el[4], 'category': el[5]} for el in products]
        return products

    def product_count_reduce(self, id_, count=1):
        con = self.connection()
        cur = con.cursor()
        product = self.get_product(id_)
        prod_count = product['count']
        if product['count'] != 0:
            prod_count = product['count'] - count
        cur.execute(f"UPDATE {product_table_name} SET productCount={prod_count} "
                    f" WHERE productID={id_};")

        con.commit()
        con.close()

    def product_count_add(self, id, count=1):
        con = self.connection()
        cur = con.cursor()
        product = self.get_product(id)
        prod_count = product['count'] + count
        cur.execute(f"UPDATE {product_table_name} SET productCount={prod_count} "
                    f" WHERE productID={id};")

        con.commit()
        con.close()

    def add_category(self, title, file):
        con = self.connection()
        cur = con.cursor()
        cur.execute(f"INSERT INTO categories(categoryTitle, categoryFile) VALUES ('{title}', '{file}')")
        self.con.commit()
        con.close()

    def delete_category(self, categoryID):
        con = self.connection()
        cur = con.cursor()
        cur.execute(f"DELETE FROM {category_table_name} WHERE categoryID={categoryID}")
        self.con.commit()
        self.logit.print_log(cur.execute(f'SELECT * FROM {category_table_name}').fetchall())
        con.close()

    def update_category(self, categoryID, title, file):
        con = self.connection()
        cur = con.cursor()
        cur.execute(f"UPDATE {category_table_name} "
                    f"SET categoryTitle='{title}', categoryFile='{file}' WHERE categoryID={categoryID};")

        con.commit()
        con.close()

    def get_category(self, categoryTitle):
        con = self.connection()
        cur = con.cursor()
        categories = cur.execute(
            f'SELECT * FROM {category_table_name} WHERE categoryTitle="{categoryTitle}"').fetchone()
        if categories:
            category = {'id': categories[0], 'title': categories[1], 'file': categories[2]}
            return category
        else:
            return None

    def get_category_by_id(self, categoryID):
        con = self.connection()
        cur = con.cursor()
        categories = cur.execute(f'SELECT * FROM {category_table_name} WHERE categoryID={categoryID}').fetchone()
        if categories:
            category = {'id': categories[0], 'title': categories[1], 'file': categories[2]}
            return category
        else:
            return None

    def get_categories(self):
        con = self.connection()
        cur = con.cursor()
        categories = cur.execute(f'SELECT * FROM {category_table_name}').fetchall()
        categories = [{'id': el[0], 'title': el[1], 'file': el[2]}
                      for el in categories if self.get_products_of_category(el[1]) != 0]
        return categories

    def get_category_title(self, title):
        con = self.connection()
        cur = con.cursor()
        categories = cur.execute(f'SELECT * FROM {category_table_name} WHERE categoryTitle={title}').fetchall()
        category = {'id': categories[0], 'title': categories[1]}
        return category

    def get_last_id(self, table):
        con = self.connection()
        cur = con.cursor()
        tables = cur.execute(f'SELECT * FROM SQLITE_SEQUENCE').fetchall()
        if table in [table[0] for table in tables]:
            return cur.execute(f'SELECT * FROM SQLITE_SEQUENCE where name="{table}"').fetchone()[1]

    def get_products_of_category(self, category_title):
        con = self.connection()
        cur = con.cursor()
        products = cur.execute(f'SELECT * FROM products WHERE categoryTitle="{category_title}"')
        return [{'id': el[0], 'title': el[1],
                 'price': el[2], 'count': el[3],
                 'file': el[4], 'category': el[5]} for el in products]
