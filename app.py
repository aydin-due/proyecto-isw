from flask import Flask, render_template,request,session
from werkzeug.utils import redirect
import json
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['DEBUG'] = True
categorias=['Argentina', 'China','Mexicana','Sonora','Saludable','Italiana','Japonesa', 'Regional','Navideño','Integral','Parrilladas','Repostería','Tailandesa','Taquiza','Panadería']

with open('static/data/usuarios.json') as f:
    dict_usuarios = json.load(f)

with open('static/data/productos.json') as f:
    dict_productos = json.load(f)

@app.route('/',methods=['GET','POST'])
def index():
    if 'username' in session:
        user = session['username']
        return render_template('index.html',username=user)
    return render_template('index.html')

@app.route('/products',methods=['GET','POST'])
def productos():
    if 'username' in session:
        user = session['username']
        email = session['email'] 
    if request.method == 'POST':
        if request.form['boton'] == 'Buscar':
            category = request.form['category']
            resultado = {k:v for (k,v) in dict_productos.items() if v['categoria']==category}
            if 'username' in session:
                return render_template('products.html',username=user,productos=resultado, categories=categorias)
            return render_template('products.html', productos=resultado, categories=categorias)
        else:
            producto = request.form['boton']
            dict_usuarios[email]['carrito'].append(producto)
            with open('static/data/usuarios.json', 'w') as fp:
                json.dump(dict_usuarios, fp)
            return render_template('products.html',username=user,productos=dict_productos, categories=categorias, error="Producto añadido al carrito.")
    else:
        if 'username' in session:
            return render_template('products.html',username=user,productos=dict_productos, categories=categorias)
        return render_template('products.html', productos=dict_productos, categories=categorias)

@app.route('/logout') 
def logout():
    if 'username' in session:
        session.pop('username',None)
        return redirect('/')

@app.route('/cart',methods=['GET','POST'])
def cart():
    if 'username' in session:
        user = session['username']
        email = session['email'] 
        if request.method == 'POST':
            producto = request.form['boton']
            dict_usuarios[email]['carrito'].remove(producto)
            with open('static/data/usuarios.json', 'w') as fp:
                json.dump(dict_usuarios, fp)
            carrito = {k:v for (k,v) in dict_productos.items() if k in dict_usuarios[email]['carrito']}
            return render_template('cart.html',username=user,productos=carrito, error="Producto eliminado del carrito.")
        else:
            carrito = {k:v for (k,v) in dict_productos.items() if k in dict_usuarios[email]['carrito']}
            return render_template('cart.html',username=user,productos=carrito)
    else:
        return render_template('cart.html', productos=None, error="Inicia sesión primero.")


@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        if email in dict_usuarios:
            if dict_usuarios[email]['password'] == request.form['password']:
                session['username'] = dict_usuarios[email]['name']
                session['email'] = email
                return redirect('/')
            else:
                return render_template('login.html',error='Contraseña incorrecta')
        else:
            return render_template('login.html',error='Correo incorrecto')
    else:
        return render_template('login.html')

@app.route('/registro',methods=['GET','POST'])
def registro():
    error=None
    if request.method == 'POST':
        name, surname, email, password = request.form['name'], request.form['surname'], request.form['email'], request.form['password']
        if email in dict_usuarios:
            return render_template('registro.html', error='Correo ya registrado')
        dict_usuarios[email]={}
        dict_usuarios[email]['name'] = name
        dict_usuarios[email]['surname'] = surname
        dict_usuarios[email]['password'] = password
        dict_usuarios[email]['carrito'] = []
        dict_usuarios[email]['pedido'] = None
        dict_usuarios[email]['admin'] = False
        with open('static/data/usuarios.json', 'w') as fp:
                json.dump(dict_usuarios, fp)
        session['username'] = name
        session['email'] = email
        return redirect('/')
    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True)