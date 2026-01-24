from http.client import responses
from os.path import split
from traceback import print_tb

from flask import Flask, session
from flask import url_for, redirect, jsonify
from flask import render_template, request
import os
from db import Users, Orders, Items, Ordered_item, Session

import uuid
from werkzeug.utils import secure_filename




app = Flask(__name__)
app.config['SECRET_KEY'] = 'FGEKG45N45$@#8$@#%'
@app.route('/')
def main():
    return render_template('index.html')

@app.route('/reg', methods=['POST','GET'])
def reg1():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        login = request.form['login']
        password = request.form['password']
        email = request.form['email']
        phone_num = request.form['tel']
        if request.form.get('isadmin') == 'on':
            isAdmin = 1
        else: isAdmin = 0
        with Session() as sess:
            find_user = sess.query(Users).filter_by(login=login).first()
            if find_user is None:
                with Session() as sess1:
                    new_us = Users(login=login,password=password,email=email,phone_num=phone_num,is_admin=isAdmin)
                    sess1.add(new_us)
                    sess1.commit()
                    return redirect(url_for('main'))
            else:
                return render_template('register.html', message='This login is used.')

@app.route('/log', methods=['POST','GET'])
def login1():
    if request.method == 'GET':
        if session.get('username') is not None:
            return redirect(url_for('profile'))
        else:
            return render_template('login.html')
    else:
        login = request.form['login']
        password = request.form['password']
        with Session() as sess:
            find_user = sess.query(Users).filter_by(login=login).first()
        if find_user is None:
                return render_template('login.html', message='Invalid login or password.')
        else:
            if find_user.password == password:
                session['id'] = find_user.id
                session['role'] = 0 if find_user.is_admin == 0 else 1
                session['username'] = login
                return redirect(url_for('main'))
            else: return render_template('login.html', message='Invalid login or password.')

@app.route('/prof', methods=['GET'])
def profile():
    user_id = session.get('id')
    if user_id is None:
        return redirect(url_for('login1'))

    if request.method == "GET":
        id = session['id']
        username = session['username']
        role = session['role']
        return render_template('profile.html',id=id,username=username, role=role)

@app.route('/logout')
def leave():
    session.clear()
    return redirect(url_for('main'))




@app.route('/shop', methods=['GET','POST'])
def shop():
    username = session.get('username')
    role = session.get('role')
    if request.method == 'GET':
        with Session() as sess:
            all_products = sess.query(Items).all()
        return render_template('shop.html',username=username, role=role,data=all_products)
    else:
        item_id = request.json['id']
        quantity = int(request.json['quantity'])


        user_cart = session.get('user_cart')
        if not user_cart:
            user_cart = []
        else:
            user_cart = list(user_cart)
        print(user_cart)

        user_cart.append([item_id,quantity])
        session['user_cart'] = user_cart
        print(user_cart)
        return jsonify({'id':item_id})




@app.route('/new_item', methods=['GET','POST'])
def new_item():
    if session.get('role') != 1:
        return redirect(url_for('main'))
    else:
        if request.method == 'GET':
            return render_template('new_item.html')
        else:
            name = request.form['name']
            price = int(request.form['price'])
            currency = request.form['currency']
            description = request.form['description']
            img_name = request.files['img']

            filename = secure_filename(img_name.filename)
            unique_name = f"{uuid.uuid4()}_{filename}"

            path = os.path.join('static/photos',unique_name)
            img_name.save(path)

        

            with Session() as sess1:
                new_item1 = Items(name=name,price=price, currency=currency,description=description,img=unique_name)
                sess1.add(new_item1)
                sess1.commit()

            return jsonify({'name':name})
                
@app.route('/cart')
def cart():
    username = session.get('username')
    if username:
        cart = session.get('user_cart')
        product_info = []
        if cart is None:
            return redirect(url_for('shop'))
        else:
            with Session() as sess:
                for i in cart:
                    info = sess.query(Items).filter_by(id=i[0]).first()
                    product_info.append([i[0],info.name,info.price,info.currency,i[1],info.description,info.img])

                    print('-'*50)
                    print(product_info)
            print(session.get('user_cart'))
            return render_template('cart.html',username=username,cart=product_info)
    else:
        return redirect(url_for('login1'))

@app.route('/order', methods=['GET'])
def order():
    cart = session.get('user_cart')
    if request.method == 'GET':
        product_info = []
        with Session() as sess:

            new_order = Orders(user_id=session.get('id'),total_price=0)
            sess.add(new_order)
            sess.commit()
            sess.refresh(new_order)
            total_price = 0
            for i in cart:
                info = sess.query(Items).filter_by(id=i[0]).first()
                total_price += i[1] * int(info.price)
                new_item = Ordered_item(order_id=new_order.id, item_id=info.id,quantity=i[1])
                sess.add(new_item)

                product_info.append([i[0], info.name, info.price, info.currency, i[1], info.description, info.img])
            else:
                new_order.total_price = total_price
                sess.commit()


        session.pop('user_cart')
        return render_template('order.html',cart=product_info,total_price=total_price)

@app.route('/remove',methods=['POST'])
def remove_item():
    if request.method == 'POST':
        item_id = request.json['id']
        with Session() as sess:
            deleted_item = sess.query(Items).filter_by(id=item_id).first()
            sess.delete(deleted_item)
            sess.commit()
        return jsonify({'id':item_id})

@app.route('/user_orders', methods=['POST','GET'])
def user_orders():
    if request.method == 'GET':
        user_id = session.get('id')
        user_info = None
        with Session() as sess:
            user_info = sess.query(Orders).filter_by(user_id=user_id).all()
        for i in user_info:
            print(i.user_id)
        return render_template('user_orders.html', orders=user_info)
    else:
        order_id = request.json['id']
        lists = ''
        with Session() as sess:
             products = sess.query(Ordered_item).filter_by(order_id=order_id).all()
             for i in products:
                tea = sess.query(Items).filter_by(id=i.item_id).first()

                lists += f'Name:{tea.name} price:{tea.price} quantity:{i.quantity}\n'



        return jsonify({'products' : lists})

@app.route('/graphs')
def graphs():
    x = []
    y = []
    with Session() as sess:
        all_info = sess.query(Orders)
    for i in all_info:
        date = str(i.date)
        day = date.split(' ')[0].split('-')[2]
        if day not in x:
            y.append(0)
            x.append(day)
        if x[-1] == day:
            y[-1] += int(i.total_price)
        else: y.append(0)
    else:
        print(x)
        print(y)

    return render_template('graphs.html')

if __name__ == "__main__":
    app.run(port=5000, debug=True)