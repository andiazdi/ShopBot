from telebot import types

candies = ['beef', 'chicken']

products = {'beef': 'мясная лапша',
            'chicken': 'куриная лапша',
            'caramel': 'Молочная конфета',
            'sugar': 'Мятная конфета'
}


def markup_noodles():
    products = types.InlineKeyboardMarkup(row_width=2)
    potato = types.InlineKeyboardButton('Мясная лапша 75р/упаковка', callback_data='get_beef_75')
    carrot = types.InlineKeyboardButton('Куриная лапша 110р/упаковка', callback_data='get_chicken_110')
    catalog = types.InlineKeyboardButton('⬅ Назад', callback_data='go_to_catalog')
    products.add(carrot, potato, catalog)

    return products


def markup_candies():
    products = types.InlineKeyboardMarkup(row_width=2)
    apple = types.InlineKeyboardButton('Молочные конфеты 104р/упаковка', callback_data='get_caramel_60')
    banana = types.InlineKeyboardButton('Мятные конфеты 119р/упаковка', callback_data='get_sugar_119')
    catalog = types.InlineKeyboardButton('⬅ Назад', callback_data='go_to_catalog')
    products.add(apple, banana, catalog)

    return products


def markup_menu():
    menu = types.ReplyKeyboardMarkup(row_width=2)
    catalog = types.KeyboardButton('💰 Каталог')
    contacts = types.KeyboardButton('👥 Контакты')
    basket = types.KeyboardButton('🛒 Корзина')
    menu.add(catalog, contacts, basket)

    return menu


def markup_catalog():
    catalog = types.InlineKeyboardMarkup(row_width=2)
    fruits = types.InlineKeyboardButton('🍜 Лапша', callback_data='go_to_noodles')
    vegetables = types.InlineKeyboardButton('🍬 Конфеты', callback_data='go_to_candies')
    catalog.add(fruits, vegetables)

    return catalog


def markup_product(product, price):
    product_menu = types.InlineKeyboardMarkup(row_width=2)
    add = types.InlineKeyboardButton('Добавить в корзину', callback_data=f'add_{product}_{price}')
    delete = types.InlineKeyboardButton('Убрать из корзины', callback_data=f'del_{product}_{price}')
    if product in candies:
        go_back = types.InlineKeyboardButton('⬅ Назад', callback_data='go_to_candies')
    else:
        go_back = types.InlineKeyboardButton('⬅ Назад', callback_data='go_to_noodles')
    product_menu.add(add, delete, go_back)

    return product_menu


def markup_basket():
    bssket = types.InlineKeyboardMarkup()
    add = types.InlineKeyboardButton(text='Оформить заказ ✅', callback_data='buy')
    bssket.add(add)

    return bssket


def markup_confirm():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='address_ok')
    bad = types.InlineKeyboardButton(text='Ввести адрес заново ❌', callback_data='address_bad')
    markup.add(ok, bad)

    return markup


def is_product_fruit(product):
    global candies

    if product in candies:
        return True
    return False


def clear_list(list):
    new_list = []
    for i in list:
        if i != '':
            new_list.append(i)
    return new_list


def cancel_buy():
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text='Отменить оформление ❌', callback_data='cancel_buy')
    markup.add(cancel)

    return markup


class Basket:
    def __init__(self):
        global products
        self.my_basket = {}
        self.products = products

    def add_user(self, user_id):
        self.my_basket[user_id] = {}

    def add_address(self, address, user_id):
        self.my_basket[user_id]['address'] = address

    def add_product(self, product, price, user_id):
        try:
            if product not in self.my_basket[user_id].keys():
                product_ru = self.products[product]
                self.my_basket[user_id][product] = [product_ru.capitalize(), 1, int(price)]
            else:
                name, count, product_price = self.my_basket[user_id][product]
                self.my_basket[user_id][product] = [name, count + 1, product_price + int(price)]
            return True

        except Exception as e:
            print(f"Error in the adding - {e}")
            return False

    def delete_product(self, product, price, user_id):
        try:
            if product in self.my_basket[user_id].keys():
                name, count, product_price = self.my_basket[user_id][product]
                if count == 0:
                    return False
                else:
                    self.my_basket[user_id][product] = [name, count - 1, product_price - int(price)]
                    if count - 1 == 0:
                        del self.my_basket[user_id][product]
                    return True

            return False
        except Exception as e:
            print(f'Error in the deleting - {e}')
            return False

    def get_product(self, product, user_id):
        try:
            if product in self.my_basket[user_id].keys():
                if product != 'address':
                    name, count, product_price = self.my_basket[user_id][product]
                    msg = f'{name} (шт): {count}, цена: {product_price} рублей'
                    return msg
        except Exception as e:
            print(f'Error in a getting the product - {e}')
            return False

    def get_basket(self, user_id):
        try:
            msg = ''
            max_length = 0
            if user_id in self.my_basket.keys():
                for i in self.my_basket[user_id].keys():
                    if i != 'address':
                        product = f'{self.get_product(i, user_id)}\n'
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
        except Exception as e:
            print(f'Error in getting a basket - {e}')
            return False

    def get_total_price(self, user_id):
        try:
            total_price = 0
            if user_id in self.my_basket.keys():
                for i in self.my_basket[user_id]:
                    if i != 'address':
                        price = self.my_basket[user_id][i][2]
                        total_price += price
                return str(total_price)
        except Exception as e:
            print(f'Error in a getting total price - {e}')

    def built_basket(self, message):
        msg = self.get_basket(message.chat.id)
        msg += '\n'
        name = f'{message.chat.first_name} {message.chat.last_name}\nusername - {message.chat.username}'
        msg += f'{name}\n'
        msg += f'Адрес - {self.my_basket[message.chat.id]["address"]}'
        return msg

    def get_price(self, product, user_id):
        if self.my_basket[user_id][product] in self.my_basket[user_id].keys():
            return self.my_basket[user_id][product][2]

    def get_count(self, product, user_id):
        try:
            if product in self.my_basket[user_id].keys():
                return self.my_basket[user_id][product][1]
            else:
                return 0
        except Exception as e:
            print(e, e.__class__.__name__)

    def get_name(self, product, user_id):
        if self.my_basket[user_id][product] in self.my_basket[user_id].keys():
            return self.my_basket[user_id][product][0]
