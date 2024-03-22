from itertools import product
from telebot import types
import sys
from pymongo import MongoClient

# sys.path.append('/home/almaz/ShopBot/db/')
sys.path.append(r'D:\\languages\\Python\\ShopBot\\db\\')
from dbActions import *

# filename = 'ShopBotLogging.log'

logger = Logger()
db = DB(db_path, logger)


class Basket:
    def __init__(self):
        global products
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.shopbot
        self.collection = self.db.collection

    def add_user(self, user_id):
        if not self.collection.find_one({"user_id": user_id}):
            self.collection.insert_one({"user_id": user_id, 'products': {}, 'address': ''})

    def add_address(self, address, user_id):
        self.collection.update_one({'user_id': user_id}, {"$set": {'address': address}})

    def add_product(self, product, user_id):
        products = self.collection.find_one({"user_id": user_id})['products']
        if f"{product['id']}" in list(products.keys()):
            count = products[f"{product['id']}"]
            if product['count'] < count + 1:
                return 'Товар закончился'
            self.collection.update_one({'user_id': user_id}, {'$set': {f'products.{product["id"]}': count + 1}})
        else:
            if product['count'] != 0:
                self.collection.update_one({'user_id': user_id}, {'$set': {f'products.{product["id"]}': 1}})
            else: return 'Товар закончился'
        return 'ok'

    def delete_product(self, product, user_id):
        products = self.collection.find_one({"user_id": user_id})['products']
        if f"{product['id']}" in list(products.keys()):
            count = products[f"{product['id']}"]
            if count == 1:
                self.collection.update_one({'user_id': user_id}, {"$unset": {f"products.{product['id']}": ''}})
            elif count != 0:
                self.collection.update_one({'user_id': user_id},
                                           {'$set': {f'products.{product["id"]}': count - 1}})
        return True

    def get_product(self, product_id, user_id):
        if f"{product_id}" in list(self.collection.find_one({"user_id": user_id})['products'].keys()):
            count = self.collection.find_one({"user_id": user_id})['products'][f"{product_id}"]
            product = db.get_product(product_id)
            msg = f'{product["title"]} (шт): {count}, цена: {count * product["price"]} рублей'
            return msg

    def get_basket(self, user_id):
        msg = ''
        max_length = 0
        if self.collection.find_one():
            for product_id in self.collection.find_one({'user_id': user_id})['products'].keys():
                product = self.get_product(product_id, user_id)
                product = f'{product}\n'
                if max_length < len(product):
                    max_length = len(product)
                msg += product
        else:
            self.add_user(user_id)
        if max_length == 0:
            return False
        msg += f'{"--" * max_length}\n'
        msg += f'Итоговая сумма: {self.get_total_price(user_id)} рублей 💵'
        return msg

    def get_total_price(self, user_id):
        total_price = 0
        if self.collection.find_one():
            products = self.collection.find_one({'user_id': user_id})['products']
            for product_id in products:
                count = products[f"{product_id}"]
                product_price = db.get_product(product_id)['price']
                price = count * product_price
                total_price += price
            return total_price

    def built_basket(self, message):
        msg = self.get_basket(message.chat.id)
        msg += '\n'
        name = f'{message.chat.first_name} {message.chat.last_name}\nusername - {message.chat.username}'
        msg += f'{name}\n'
        address = self.collection.find_one({'user_id': message.chat.id})["address"]
        msg += f'Адрес - {address}'
        return msg

    def get_count(self, product, user_id):
        try:
            return self.collection.find_one({'user_id': user_id})['products'][f'{product["id"]}']
        except:
            return 0

    def clear_basket(self, user_id):
        self.collection.update_one({'user_id': user_id}, {'$set': {'products': {}}})

    def get_products(self, user_id):
        return self.collection.find_one({'user_id': user_id})['products']


def markup_menu():
    menu = types.ReplyKeyboardMarkup(row_width=2)
    catalog = types.KeyboardButton('💰 Каталог')
    contacts = types.KeyboardButton('👥 Контакты')
    basket = types.KeyboardButton('🛒 Корзина')
    menu.add(catalog, contacts, basket)

    return menu


def markup_catalog():
    categories = db.get_categories()
    catalog = types.InlineKeyboardMarkup()
    for item in categories:
        button = types.InlineKeyboardButton(item['title'], callback_data=f'go_to_category_{item["id"]}')
        catalog.add(button)

    return catalog


def markup_category(category):
    products = types.InlineKeyboardMarkup(row_width=2)
    elements = []
    for product in db.get_products_of_category(category['title']):
        elements.append(types.InlineKeyboardButton(f'{product["title"]} {product["price"]}р',
                                                   callback_data=f'get_product_{product["id"]}'))
    elements.append(types.InlineKeyboardButton('⬅ Назад', callback_data='go_to_catalog'))
    products.add(*elements)

    return products


def markup_product(product):
    product_menu = types.InlineKeyboardMarkup(row_width=2)
    add = types.InlineKeyboardButton('Добавить в корзину', callback_data=f'add_product_{product["id"]}')
    delete = types.InlineKeyboardButton('Убрать из корзины', callback_data=f'del_product_{product["id"]}')
    back = types.InlineKeyboardButton('⬅ Назад',
                                         callback_data=f'go_to_category_'
                                                       f'{db.get_category(product["category"])["id"]}')
    product_menu.add(add, delete, back)

    return product_menu


def markup_basket():
    basket = types.InlineKeyboardMarkup()
    add = types.InlineKeyboardButton(text='Оформить заказ ✅', callback_data='buy')
    clear = types.InlineKeyboardButton(text='Очистить корзину ❌', callback_data='clear_basket')
    basket.add(add, clear)

    return basket


def markup_confirm():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='address_ok')
    bad = types.InlineKeyboardButton(text='Ввести адрес заново ❌', callback_data='address_bad')
    bad = types.InlineKeyboardButton(text='Отменить оформление заказа ❌', callback_data='cancel_buy')
    markup.add(ok, bad)

    return markup


def cancel_buy():
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text='Отменить оформление ❌', callback_data='cancel_buy')
    markup.add(cancel)

    return markup

