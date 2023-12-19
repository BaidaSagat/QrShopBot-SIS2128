from sqlalchemy.orm import joinedload

from DB.tables import User, Category, Product, Cart, async_session
from sqlalchemy import select, delete

async def get_categories(): # Get categories from DB
    async with async_session() as session:
        result = await session.scalars(select(Category))
        return result

async def get_products(category_id): # Get products from DB
    async with async_session() as session:
        result = await session.scalars(select(Product).where(Product.category_id == category_id))
        return result

async def get_product(product_id): # Get a sprecific product from DB
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().one()
        return product

async def get_cart(user_id): # Get user cart from DB
    async with async_session() as session:
        result = await session.scalars(select(Cart).options(joinedload(Cart.product)).where(Cart.user_id == user_id))
        return result
async def store_cart(user_id, product_id, size): # Store user cart in DB
    async with async_session() as session:
        cart = Cart(user_id=user_id, product_id=product_id, size=size)
        session.add(cart)
        await session.commit()

async def delete_cart(user_id): # Delete user cart from DB
    async with async_session() as session:
        await session.execute(delete(Cart).where(Cart.user_id == user_id))
        await session.commit()

async def update_product(product): # Update product amount in DB
    async with async_session() as session:
        db_product = await session.get(Product, product.id)
        db_product.amount = product.amount
        await session.commit()