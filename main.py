from flask import Flask, request, redirect, url_for, render_template, flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key' 

db = SQLAlchemy(app)
app.app_context().push()

# 使用者資料庫
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # is_admin = db.Column(db.Boolean, default=False)
    def __init__(self,username, email,password):
        # self.sn = sn
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

# 管理者資料庫
class Admin(db.Model):
    adminid = db.Column(db.Integer, primary_key=True)
    adminname = db.Column(db.String(80), unique=True, nullable=False)
    adminemail = db.Column(db.String(120), unique=True, nullable=False)
    adminpassword = db.Column(db.String(120), nullable=False)
    def __init__(self, adminname, adminemail,adminpassword):
        # self.adminid = adminid
        self.adminname = adminname
        self.adminemail = adminemail
        self.adminpassword = adminpassword

    def __repr__(self):
        return '<Admin %r>' % self.adminname

# 商品資料庫
class Item(db.Model):
    itemid = db.Column(db.Integer, primary_key=True)
    
    itemname = db.Column(db.String(120), unique=True, nullable=False)
    itemprice = db.Column(db.String(120), nullable=False)
    def __init__(self,itemname,itemprice):
        self.itemname= itemname
        self.itemprice = itemprice

    def __repr__(self):
        return '<Item %r>' % self.itemname

# 購物車資料庫
class Cart(db.Model):
    cartid = db.Column(db.Integer, primary_key=True)
    cartuser = db.Column(db.String(80), nullable=False)
    cartname = db.Column(db.String(120), nullable=False)
    cartprice = db.Column(db.String(80), nullable=False)
    cartquantity = db.Column(db.Integer, nullable=False)
    def __init__(self, cartuser, cartname,cartprice,cartquantity):
        self.cartuser = cartuser
        self.cartname= cartname
        self.cartprice = cartprice
        self.cartquantity = cartquantity

    def __repr__(self):
        return '<Cart %r>' % self.cartuser

# 訂單資料庫
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orderid = db.Column(db.Integer, unique=True, nullable=False)
    orderuser = db.Column(db.String(80), nullable=False)
    totalprice = db.Column(db.Integer, nullable=False)
    totalquantity = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __init__(self,orderid, orderuser, totalprice,totalquantity):
        self.orderid = orderid
        self.orderuser = orderuser
        self.totalprice= totalprice
        self.totalquantity = totalquantity
        
    def __repr__(self):
        return '<Order %r>' % self.orderuser

# 訂單詳情資料庫
class Orderitem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orderitemid = db.Column(db.Integer, nullable=False)
    orderitemname = db.Column(db.String(80), nullable=False)
    orderitemprice = db.Column(db.Integer, nullable=False)
    orderitemquantity = db.Column(db.Integer, nullable=False)
    orderitemsudtotal = db.Column(db.Integer, nullable=False)
    def __init__(self,orderitemid, orderitemname, orderitemprice,orderitemquantity,orderitemsudtotal):
        self.orderitemid = orderitemid
        self.orderitemname = orderitemname
        self.orderitemprice = orderitemprice
        self.orderitemquantity= orderitemquantity
        self.orderitemsudtotal = orderitemsudtotal
        
    def __repr__(self):
        return '<Orderitem %r>' % self.orderitemid

with app.app_context():
    db.create_all()


#管理者帳密
# admin = Admin('lucy','lucy@gmail','960525')
# db.session.add(admin)
# db.session.commit()
# app.logger.info(Admin.adminid)

# 會員註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # 檢查是否已存在用戶名或電子郵件
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('此帳號或用戶名已有人使用', 'danger')
            return redirect(url_for('register'))

        # 創建新用戶並插入資料庫
        new_user = User(username=username, email=email, password=password)
        try:
            # 加入資料庫
            db.session.add(new_user)
            db.session.commit()
            flash('註冊成功! 開始登入', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed. Error: {e}', 'danger')

    return render_template('register.html')

# 會員登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 先將暫存區清空
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    # 取得回復資料
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # 檢查用戶是否存在
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            # 將用戶資料放入暫存區
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            return redirect(url_for('head', username=session['username']))
        # 若不存在，則回報帳密錯誤
        else:
            flash('帳號或密碼錯誤', 'danger')
    return render_template('login.html')
    
# 管理者登入    
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        adminemail = request.form['adminemail']
        adminpassword = request.form['adminpassword']

        adminuser = Admin.query.filter_by(adminemail=adminemail, adminpassword=adminpassword).first()
        if adminuser:
            return redirect(url_for('adminindex'))
        else:
            flash('帳號或密碼錯誤', 'danger')

    return render_template('adminlogin.html')

# 管理者模式/首頁
@app.route('/adminindex')
def adminindex():
    usernumber = User.query.count()
    itemnumber = Item.query.count()
    ordernumber = Order.query.count()
    return render_template("adminindex.html",usernumber=usernumber,itemnumber=itemnumber,ordernumber=ordernumber)

# 管理者模式/所有訂單
@app.route('/allorders')
def allorders():
    allorders = Order.query.all()
    return render_template("allorders.html", allorders= allorders)

# 管理者模式/所有訂單/訂單詳情
@app.route('/adminorder_details/<int:orderid>')
def adminorder_details(orderid):
    order = Order.query.get(orderid)
    if not order:
        return redirect(url_for('orders'))

    order_items = Orderitem.query.filter_by(orderitemid=orderid).all()
    return render_template('adminorder_details.html', order=order, order_items=order_items)
    
# 管理者模式/所有用戶
@app.route('/allusers')
def allusers():
    allusers = User.query.all()
    return render_template("allusers.html", allusers= allusers)

#訪客模式/首頁
@app.route('/index')
def index():
    return render_template("index.html")

# 訪客模式/All items頁面
@app.route('/allitems0')
def allitems0():
    return render_template("allitems0.html")

# 訪客模式/角色故事
@app.route('/story0')
def story0():
    return render_template("story0.html")

# 會員模式/首頁
@app.route('/head')
def head():
    return render_template("head.html", username=session['username'])

# 會員登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    return render_template("index.html")

# 會員模式/All items頁面
@app.route('/allitems')
def allitems():
    return render_template("allitems.html", username=session['username'])

# 會員模式/All items頁面/加入購物車
@app.route('/add_to_cart/<string:itemname>')
def add_to_cart(itemname):
    if 'username' not in session:
        return redirect(url_for('login'))

    cartuser = session['username']
    itemprice1 = Item.query.filter_by(itemname=itemname).first()
    cartprice = itemprice1.itemprice
    cart_item = Cart.query.filter_by(cartuser=cartuser, cartname=itemname).first()
    if cart_item:
        cart_item.cartquantity += 1
    else:
        cart_item = Cart(cartuser=cartuser, cartname=itemname, cartprice=cartprice,cartquantity = 1)
        
    db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('allitems'))

# 會員模式/購物車/刪除
@app.route('/delete_to_cart/<string:cartname>')
def delete_to_cart(cartname):
    if 'username' not in session:
        return redirect(url_for('login'))

    cartuser = session['username']
    cart_item = Cart.query.filter_by(cartuser=cartuser, cartname=cartname).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('cart'))

# 會員模式/角色故事
@app.route('/story')
def story():
    return render_template("story.html", username=session['username'])


# 會員模式/購物車
@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    cartuser = session['username']
    cart_items = Cart.query.filter_by(cartuser=cartuser).all()
    return render_template("cart.html",username=session['username'], cart_items=cart_items)

# 會員模式/購物車/去買單
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))

    orderuser = session['username']
    cart_items = Cart.query.filter_by(cartuser=orderuser).all()

    if not cart_items:
        return redirect(url_for('cart'))
        
    orderid = Order.query.count() + 1
    totalprice = sum(int(item.cartprice) * item.cartquantity for item in cart_items)
    totalquantity = sum(item.cartquantity for item in cart_items)
    new_order = Order(orderid=orderid,orderuser=orderuser, totalprice=totalprice,totalquantity = totalquantity)

    db.session.add(new_order)
    db.session.commit()
    orderitemid =new_order.orderid
    
    for item in cart_items:
        orderitemid =new_order.orderid
        orderitemname = item.cartname
        orderitemprice=int(item.cartprice)
        orderitemquantity= item.cartquantity 
        orderitemsudtotal=orderitemprice * orderitemquantity
        order_item = Orderitem(orderitemid, orderitemname, orderitemprice, orderitemquantity,orderitemsudtotal)
        db.session.add(order_item)
        db.session.delete(item)  
        
    db.session.commit()
    return redirect(url_for('orders'))

# 會員模式/我的訂單
@app.route('/orders')
def orders():
    if 'username' not in session:
        return redirect(url_for('login'))

    orderuser = session['username']
    orders = Order.query.filter_by(orderuser=orderuser).all()
    return render_template('orders.html', orders=orders, username=session['username'])

# 會員模式/我的訂單/訂單詳情
@app.route('/order_details/<int:orderid>')
def order_details(orderid):
    if 'username' not in session:
        return redirect(url_for('login'))

    order = Order.query.get(orderid)
    if not order:
        return redirect(url_for('orders'))

    order_items = Orderitem.query.filter_by(orderitemid=orderid).all()
    return render_template('order_details.html', order=order, order_items=order_items, username=session['username'])



if __name__ == '__main__':
    app.debug = True
    app.run()