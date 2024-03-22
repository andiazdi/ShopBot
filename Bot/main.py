import telebot
from telebot.types import LabeledPrice, ShippingOption
from functions import *
from config import *

logger.print_log('App is running')
bot = telebot.TeleBot(bot_token)
temp = {}
basket = Basket()


def get_address(msg):
    basket.add_address(msg.text, msg.chat.id)
    bot.delete_message(msg.chat.id, temp[msg.chat.id])
    del temp[msg.chat.id]
    bot.send_message(msg.chat.id, f'Подтвердите адрес: {msg.text}', reply_markup=markup_confirm())


@bot.message_handler(commands=['start'])
def start(message):
    basket.add_user(message.chat.id)
    msg = f'Приветствую, {message.from_user.first_name}, в нашем магазине.\n\n'
    msg += '📌 Нажмите "Каталог" чтобы выбрать товары.\n'
    msg += '📌 Нажмите "Контакты" чтобы задать вопрос.\n'
    msg += '📌 Нажмите "Корзина" чтобы посмотреть выбранные товары.\n\n'
    msg += 'Важно, бот тестируется и в нем еще нет онлайн оплаты, она осуществляется по получению. ' \
           'А также бесплатная доставка только по Иннополису (бессплатная доставка в Казани от 3000 рублей)\n'
    bot.send_message(message.chat.id, msg, reply_markup=markup_menu())
    info = f'{message.chat.id} started ShopBot'
    logger.print_log(info)


@bot.message_handler(content_types=['text'])
def text(message):
    basket.add_user(message.chat.id)
    
    if message.text == '💰 Каталог':
        bot.send_message(message.chat.id, 'Выберите нужную категорию:', reply_markup=markup_catalog())
    
    if message.text == '👥 Контакты':
        msg = 'Наши контакты:\n\n'
        msg += '✉ Телеграм - @AlmazAndukov\n'
        msg += '☎ Контактный номер - 89869264375'
        bot.send_message(message.chat.id, msg)
    
    if message.text == '🛒 Корзина':
        msg = basket.get_basket(message.chat.id)
        if msg:
            bot.send_message(message.chat.id, msg, reply_markup=markup_basket())
        else:
            bot.send_message(message.chat.id, 'Корзина ещё пуста, советую открыть каталог 😉')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global products, candies, basket
    basket.add_user(call.message.chat.id)
    if call.message:
        if 'buy' == call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            msg = bot.send_message(call.message.chat.id, 'Введите адрес доставки ✈:', reply_markup=cancel_buy())
            temp[call.message.chat.id] = msg.message_id
            bot.register_next_step_handler(msg, get_address)
        
        elif 'cancel_buy' == call.data:
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Выберите нужную категорию:', reply_markup=markup_catalog())
        
        elif 'go_back' == call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)

        elif 'clear_basket' == call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Корзина успешно очищена ✅')
            bot.send_message(call.message.chat.id, 'Выберите нужную категорию:', reply_markup=markup_catalog())
            basket.clear_basket(call.message.chat.id)
        
        elif 'add_product_' in call.data:
            product_id = int(call.data.split('_')[-1])
            product = db.get_product(product_id)
            add = basket.add_product(product, call.message.chat.id)
            if add == 'ok':
                try:
                    msg = f'Успешное добавление'
                    msg = f'{msg}. В корзине - {basket.get_count(product, call.message.chat.id)} ({product["title"]})'
                except:
                    print('ERROR')
                bot.answer_callback_query(call.id, show_alert=False, text=msg)
            elif add == 'Товар закончился':
                msg = 'К сожалению, товар закончился'
                bot.answer_callback_query(call.id, show_alert=False, text=msg)
            else:
                msg = f'Неудачная попытка добавления {product["title"]} в корзину'
                bot.answer_callback_query(call.id, show_alert=False, text=msg)

        elif 'del_product_' in call.data:
            _, product, price = call.data.split('_')
            product_id = int(call.data.split('_')[-1])
            product = db.get_product(product_id)
            add = basket.delete_product(product, call.message.chat.id)
            if add:
                try:
                    msg = f'Успешное удаления'
                    msg = f'{msg}. В корзине - {basket.get_count(product, call.message.chat.id)} ({product["title"]})'
                except:
                    print('ERROR')
                bot.answer_callback_query(call.id, show_alert=False, text=msg)
            else:
                msg = f'Неудачная попытка удаления {product["title"]} в корзину'
                bot.answer_callback_query(call.id, show_alert=False, text=msg)
        
        elif 'get_product_' in call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            product_id = int(call.data.split('_')[-1])
            product = db.get_product(product_id)
            bot.send_photo(call.message.chat.id,
                           open(f'{path}/AdminPanel'
                                f'/static/images/products/{product["file"]}', 'rb'),
                           reply_markup=markup_product(product))
        
        elif 'go_to_category_' in call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            category_id = (call.data.split('_')[-1])
            category = db.get_category_by_id(category_id)
            bot.send_photo(call.message.chat.id,
                           open(f'{path}/AdminPanel/static/images/categories/{category["file"]}',
                                'rb'), reply_markup=markup_category(category))

        elif 'go_to_catalog' == call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Выберите нужную категорию:', reply_markup=markup_catalog())
    
        elif 'address_' in call.data:
            _, status = call.data.split('_')
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if status == 'ok':
                prices = []
                products = basket.get_products(call.message.chat.id)
                for product_id in list(products.keys()):
                    product_ = db.get_product(product_id)
                    title = product_['title']
                    price = product_['price'] * products[product_id] * 1000
                    prices.append(LabeledPrice(label=title, amount=price))
                bot.send_invoice(call.message.chat.id, title='У Алмаза',
                                 description='Test description',
                                 provider_token=provider_token,
                                 currency='rub',
                                 photo_url='https://sun9-48.userapi.com/impf/cNhSeTtDz7he5-L4ew5KeuJ7IOJBgIWaCkAUuQ/1T3Hzt3IvH4.jpg?size=959x959&quality=96&sign=0d10bb3218ab8fd1d09bdd99aeffd708&type=album',
                                 photo_height=512,  # !=0/None or picture won't be shown
                                 photo_width=512,
                                 photo_size=512,
                                 is_flexible=False,  # True If you need to set up Shipping Fee
                                 prices=prices,
                                 start_parameter='time-machine-example',
                                 invoice_payload='HAPPY FRIDAYS COUPON')
            else:
                msg = bot.send_message(call.message.chat.id, 'Введите адрес заново:')
                bot.register_next_step_handler(msg, get_address)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    msg = basket.built_basket(message)
    bot.send_message(admin_chat, msg)
    bot.send_message(message.chat.id, 'Ваш заказ оформляется и будет доставлен в ближайшее время 😉')
    products = basket.get_products(message.chat.id)
    for product_id in list(products.keys()):
        count = products[f"{product_id}"]
        db.product_count_reduce(int(product_id), count)
    basket.clear_basket(message.chat.id)
    info = f'{message.chat.id} bought'
    logger.print_log(info)


bot.polling(none_stop=True)