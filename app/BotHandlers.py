from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from DB.SQLRequests import get_product, store_cart, get_cart, get_products, delete_cart, update_product

import app.buttons as kb

router = Router() # Router initialization (connect to main.py)

user_states = {} # User states dictionary (for storing user states)


@router.message(CommandStart()) # Handler for /start command
async def start(message: Message):
    await message.answer('Добро пожаловать!')
    await message.answer('Я бот, который поможет вам сделать заказ в нашем магазине!', reply_markup=kb.main)

@router.message(F.text == '👕 Каталог') # Handler for 'Каталог' button
async def catalog(message: Message):
    await message.answer('Выберите категорию', reply_markup=await kb.categories())

@router.callback_query(F.data.startswith('category_')) # Handler for category selection
async def category_selected(callback: CallbackQuery):
    category_id = callback.data.split('_')[1] # Get category id from callback data
    products = await get_products(category_id) # Get products from DB
    if all(product.amount == 0 for product in products): # If all products are unavailable
        await callback.answer('В данной категории товары сейчас недоступны', show_alert=True)
        return
    else:
        user_states[callback.from_user.id] = f'category_{category_id}' # Save user state
        await callback.message.answer('Товары по выбранной категории', reply_markup=await kb.products(category_id)) # Products display
        await callback.answer('') # Answer to callback

@router.callback_query(F.data.startswith('product_')) # Handler for product selection
async def product_selected(callback: CallbackQuery):
    product_id = callback.data.split('_')[1] # Get product id from callback data
    product = await get_product(product_id) # Get product from DB
    if product.amount == 0: # If product is unavailable
        await callback.answer('Данный товар сейчас недоступен', show_alert=True)
        return
    else:
        user_states[callback.from_user.id] = f'product_{product_id}' # Save user state
        await callback.message.answer_photo(photo=product.image_url, caption=f'{product.name}\n{product.description}\nЦена: {product.price} тенге', reply_markup=await kb.product_options(product_id))
        await callback.answer('') # Answer to callback

@router.callback_query(F.data.startswith('back_')) # Handler for 'Go Back' button
async def go_back(callback: CallbackQuery): # Go back to previous state
    current_state = user_states.get(callback.from_user.id, '') # Get current user state
    if current_state.startswith('category_'): # If current state is category selection
        await callback.message.answer('Выберите категорию', reply_markup=await kb.categories())
    elif current_state.startswith('product_'): # If current state is product selection
        category_id = current_state.split('_')[1]
        await callback.message.answer('Товары по выбранной категории', reply_markup=await kb.products(category_id))
    await callback.answer('')

@router.callback_query(F.data.startswith('buy_')) # Handler for 'Купить' button
async def buy_product(callback: CallbackQuery):
    product_id = callback.data.split('_')[1] # Get product id from callback data
    user_id = callback.from_user.id # Get user id
    user_states[user_id] = f'product_{product_id}_size' # Save user state
    await callback.message.answer('Пожалуйста выберите размер изделия', reply_markup=await kb.sizes())

@router.callback_query(F.data.startswith('size_')) # Handler for size selection
async def size_selected(callback: CallbackQuery):
    size = callback.data.split('_')[1] # Get size from callback data
    user_id = callback.from_user.id # Get user id
    state = user_states[user_id] # Get user state
    if state.startswith('product_'): # If user state is product selection
        product_id = int(state.split('_')[1]) # Get product id from user state
        await store_cart(user_id, product_id, size) # Store cart item in DB
        await callback.answer('Товар добавлен в корзину', show_alert=True)

@router.message(F.text == '🛒 Корзина' or F.data == 'cart')
async def show_cart(message: Message):
    user_id = message.from_user.id # Get user id
    cart_items = await get_cart(user_id) # Get cart items from DB
    cart_message = "" # Initializing cart message variable
    for i, item in enumerate(cart_items, start=1): # Looping through cart items
        product = await get_product(item.product_id) # Get product from DB
        cart_message += f'{i}. {product.name} - {item.size} Цена: {product.price} тенге\n' # Add product info to cart message
    if cart_message: # If cart is not empty
        await message.answer(cart_message, reply_markup=await kb.cart())
    else:
        await message.answer('Ваша корзина пуста!') # If cart is empty

@router.callback_query(F.data == 'clear_cart') # Handler for 'Очистить корзину' button
async def clear_cart(callback: CallbackQuery):
    user_id = callback.from_user.id # Get user id
    await delete_cart(user_id) # Delete cart items from DB
    await callback.answer('Корзина очищена!')

@router.callback_query(F.data == 'order') # Handler for 'Оформить заказ' button
async def checkout(callback: CallbackQuery):
    user_id = callback.from_user.id # Get user id
    cart_items = await get_cart(user_id) # Get cart items from DB
    total_price = sum(item.product.price for item in cart_items) # Calculate total price
    await callback.message.answer(f'К оплате: {total_price} тенге\nВы подтверждаете этот заказ?', reply_markup=await kb.checkout())

@router.callback_query(F.data == 'pay') # Handler for 'Оплатить' button
async def confirm_purchase(callback: CallbackQuery):
    user_id = callback.from_user.id # Get user id
    cart_items = await get_cart(user_id) # Get cart items from DB
    for item in cart_items: # Looping through cart items
        product = await get_product(item.product_id) # Get product from DB
        product.amount -= 1 # Decrease product amount
        await update_product(product) # Update product amount in DB
    await delete_cart(user_id) # Delete cart items from DB (after buying)
    await callback.message.answer('Заказ оформлен, Спасибо за покупку!')

@router.callback_query(F.data == 'cancel') # Handler for 'Отменить' button
async def cancel_checkout(callback: CallbackQuery):
    user_id = callback.from_user.id # Get user id
    await show_cart(callback.message)
    await callback.answer('Заказ отменен!')

@router.message(F.text == '📞 Контакты') # Handler for 'Контакты' button
async def contacts(message: Message):
    await message.answer('Наш номер телефона: +7(707)447-64-70\nНаша почта: baidasagat@mail.ru')