from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from DB.SQLRequests import get_categories, get_products
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[ # Main keyboard
    [KeyboardButton(text='👕 Каталог')],
    [KeyboardButton(text='📞 Контакты')],
    [KeyboardButton(text='🛒 Корзина')]
], resize_keyboard=True, input_field_placeholder='Выберите пункт ниже', one_time_keyboard=False)

async def categories(): # Categories keyboard
    categories_kb = InlineKeyboardBuilder() # InlineKeyboardBuilder initialization
    categories = await get_categories() # Get categories from DB
    for category in categories: # Add categories to keyboard
        categories_kb.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    return categories_kb.adjust(2).as_markup() # Return keyboard

async def products(category_id): # Products keyboard
    products_kb = InlineKeyboardBuilder()
    products = await get_products(category_id)
    for product in products:
        products_kb.add(InlineKeyboardButton(text=product.name, callback_data=f'product_{product.id}'))
    return products_kb.adjust(2).as_markup()

async def product_options(product_id): # Product options keyboard
    options_kb = InlineKeyboardBuilder()
    options_kb.add(InlineKeyboardButton(text='Купить', callback_data=f'buy_{product_id}'))
    options_kb.add(InlineKeyboardButton(text='Назад', callback_data=f'back_{product_id}'))
    return options_kb.adjust(2).as_markup()

async def sizes(): # Sizes keyboard
    sizes_kb = InlineKeyboardBuilder()
    sizes_kb.add(InlineKeyboardButton(text='XS', callback_data='size_XS'))
    sizes_kb.add(InlineKeyboardButton(text='S', callback_data='size_S'))
    sizes_kb.add(InlineKeyboardButton(text='M', callback_data='size_M'))
    sizes_kb.add(InlineKeyboardButton(text='L', callback_data='size_L'))
    sizes_kb.add(InlineKeyboardButton(text='XL', callback_data='size_XL'))
    sizes_kb.add(InlineKeyboardButton(text='XXL', callback_data='size_XXL'))
    return sizes_kb.adjust(2).as_markup()

async def cart(): # Cart keyboard
    cart_kb = InlineKeyboardBuilder()
    cart_kb.add(InlineKeyboardButton(text='Оформить заказ', callback_data='order'))
    cart_kb.add(InlineKeyboardButton(text='Очистить корзину', callback_data='clear_cart'))
    return cart_kb.adjust(2).as_markup()

async def checkout(): # Checkout keyboard
    checkout_kb = InlineKeyboardBuilder()
    checkout_kb.add(InlineKeyboardButton(text='Оплатить', callback_data='pay'))
    checkout_kb.add(InlineKeyboardButton(text='Отменить', callback_data='cancel'))
    return checkout_kb.adjust(2).as_markup()