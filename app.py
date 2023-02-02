import os
from flask import Flask,render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable = False)
    price = db.Column(db.Integer, nullable = False)
    photo = db.Column(db.String, nullable = False) 

    def __repr__(self):
        return f'Title: {self.title}, Price: {self.price}'

def allowed_file(filename):
    return '.' in filename and \
           filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/home')
def index():
    items = Item.query.order_by(Item.id).all()


    return render_template('index.html',data=items)

@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
        secret_key='test')
    checkout = Checkout(api=api)
    data = {
    "currency": "USD",
    "amount": str(item.price) + '00'
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)

@app.route('/create', methods = ['GET','POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))   
        
        item = Item(title=title,price=price,photo=filename)

        db.session.add(item)
        db.session.commit()

        return redirect('/home')

    else:
        return render_template('create.html')


db.create_all()
if __name__ == '__main__':
    app.run(debug=True)

