from datetime import timezone
from typing import List, Optional
from xmlrpc.client import DateTime

from sqlalchemy import Table, Column, create_engine, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase , sessionmaker, Mapped, mapped_column, relationship
from datetime import datetime


engine = create_engine('sqlite:///database.db', echo=True)
Session =sessionmaker(bind=engine)

class Base(DeclarativeBase):
    def create_db(self):
        Base.metadata.create_all(engine)
    def drop_db(self):
        Base.metadata.drop_all(engine)

class Items(Base):
    __tablename__ = 'items'
    __table_args__ = {'sqlite_autoincrement': True}
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(90))
    price : Mapped[int] = mapped_column()
    currency : Mapped[str] = mapped_column(String(10))
    description : Mapped[str] = mapped_column(String(1000))
    img : Mapped[str] = mapped_column(String(200))


    items : Mapped['Ordered_item'] = relationship(back_populates='item')

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}
    id : Mapped[int] = mapped_column(primary_key=True)
    login : Mapped[str] = mapped_column(String(25))
    password : Mapped[str] = mapped_column(String(50))
    email : Mapped[str] = mapped_column(String(50))
    phone_num : Mapped[str] = mapped_column(String(20))
    is_admin : Mapped[bool] = mapped_column(Boolean, nullable=True)

    orders : Mapped['Orders'] = relationship(back_populates='user')

class Ordered_item(Base):
    __tablename__ = 'orders_items'
    __table_args__ = {'sqlite_autoincrement': True}
    id : Mapped[int] = mapped_column(primary_key=True)
    order_id : Mapped[int] = mapped_column(ForeignKey('orders.id'))
    item_id : Mapped[int] = mapped_column(ForeignKey('items.id', ondelete='SET NULL'), nullable=True)
    quantity : Mapped[int] = mapped_column()

    item : Mapped["Items"] = relationship(back_populates='items')
    orders_id : Mapped["Orders"] = relationship(back_populates='orders')

class Orders(Base):
    __table_args__ = {'sqlite_autoincrement': True}
    __tablename__ = 'orders'
    id : Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow())
    total_price : Mapped[str] = mapped_column()

    orders : Mapped['Ordered_item'] = relationship(back_populates='orders_id')
    user: Mapped["Users"] = relationship(back_populates='orders')



base = Base()
base.create_db()
# base.drop_db()

