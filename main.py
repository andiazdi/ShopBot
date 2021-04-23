import telebot
from functions import *
import logging

logging.basicConfig(level=logging.INFO, filename='ShopBotLogging.log')
logger = logging.getLogger('Logger')


logger.info('App is running')
bot = telebot.TeleBot('1642629677:AAHs3L6nV8rnJHE7MZxyw-sZJHH8C07BBNQ')
products = {'beef': 'мясная лапша',
            'chicken': 'куриная лапша',
            'caramel': 'Молочная конфета',
            'sugar': 'Мятная конфета'
}
basket = Basket()


def get_address(msg):
    basket.add_address(msg.text, msg.chat.id)
    bot.send_message(msg.chat.id, f'Подтвердите адрес: {msg.text}', reply_markup=markup_confirm())


@bot.message_handler(commands=['start'])
def start(message):
    basket.add_user(message.chat.id)
    msg = f'Приветствую, {message.from_user.first_name}, в нашем магазине.\n\n'
    msg += '📌 Нажмите "Каталог" чтобы выбрать товары.\n'
    msg += '📌 Нажмите "Контакты" чтобы задать вопрос.\n'
    msg += '📌 Нажмите "Корзина" чтобы посмотреть выбранные товары.\n'
    bot.send_message(message.chat.id, msg, reply_markup=markup_menu())
    info = f'{message.chat.id} started ShopBot'
    logger.info(info)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == '💰 Каталог':
        bot.send_message(message.chat.id, 'Выберите нужную категорию:', reply_markup=markup_catalog())
    if message.text == '👥 Контакты':
        msg = ''
        msg += 'Наши контакты:\n\n'
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
    try:
        if call.message:
            if 'buy' == call.data:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                msg = bot.send_message(call.message.chat.id, 'Введите адрес доставки ✈:', reply_markup=cancel_buy())
                bot.register_next_step_handler(msg, get_address)
            elif 'cancel_buy' == call.data:
                bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, 'Выберите нужную категорию:', reply_markup=markup_catalog())
            elif 'go_back' == call.data:
                bot.delete_message(call.message.chat.id, call.message.message_id)

            elif 'add_' in call.data:
                _, product, price = call.data.split('_')
                add = basket.add_product(product, price, call.message.chat.id)
                if add:
                    msg = f'Успешное добавление {products[product]}'
                    msg = f'{msg}. В корзине - {basket.get_count(product, call.message.chat.id)} ({products[product]})'
                    bot.answer_callback_query(call.id, show_alert=False, text=msg)
                else:
                    msg = f'Неудачная попытка добавления {products[product]} в корзину'
                    bot.answer_callback_query(call.id, show_alert=False, text=msg)

            elif 'del_' in call.data:
                _, product, price = call.data.split('_')
                delete = basket.delete_product(product, price, call.message.chat.id)
                if delete:
                    msg = 'Успешное удаление из корзины'
                    msg = f'{msg}. В корзине - {basket.get_count(product, call.message.chat.id)} ({products[product]})'
                    bot.answer_callback_query(call.id, show_alert=False, text=msg)
                else:
                    bot.answer_callback_query(call.id, show_alert=False, text=f'Неудачная попытка удаление {products[product]} из корзины')

            elif 'get_' in call.data:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                _, product, price = call.data.split('_')
                # is_fruit = is_product_fruit(product)
                bot.send_photo(call.message.chat.id, open(f'{product}.png', 'rb'), reply_markup=markup_product(product, price))

            elif 'go_to_candies' == call.data:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_photo(call.message.chat.id, open('candies.png', 'rb'), reply_markup=markup_candies())

            elif 'go_to_noodles' == call.data:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_photo(call.message.chat.id, open('noodles.jpg', 'rb'), reply_markup=markup_noodles())

            elif 'go_to_catalog' == call.data:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, 'Выберите нужную категорию:', reply_markup=markup_catalog())
            elif 'address_' in call.data:
                _, status = call.data.split('_')
                bot.delete_message(call.message.chat.id, call.message.message_id)
                if status == 'ok':
                    msg = basket.built_basket(call.message)
                    bot.send_message(-496190531, msg)
                    bot.send_message(call.message.chat.id, 'Ваш заказ оформляется и'
                                                           ' будет доставлен в ближайшее время 😉')
                    info = f'{call.message.chat.id} bought'
                    logger.info(info)
                else:
                    msg = bot.send_message(call.message.chat.id, 'Введите адрес заново:')
                    bot.register_next_step_handler(msg, get_address)

    except Exception as e:
        print(e)


bot.polling(none_stop=True)
