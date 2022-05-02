from flask import Flask, render_template,request,session
from werkzeug.utils import redirect
import json
import os
import secrets
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['DEBUG'] = True
categorias=['Argentina', 'China','Mexicana','Sonora','Saludable','Italiana','Japonesa', 'Regional','Navideño','Integral','Parrilladas','Repostería','Tailandesa','Taquiza','Panadería']

with open('static/data/usuarios.json') as f:
    dict_usuarios = json.load(f)

with open('static/data/productos.json') as f:
    dict_productos = json.load(f)

@app.route("/", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        error = ''
        producto = request.form['producto']
        resultados = {k:v for k,v in dict_productos.items() if (producto.lower() in v['title'].lower())}
        if (len(resultados.keys())<0):
            error = 'No se encontraron productos'
        if 'username' in session:
            user = session['username']
            return render_template('index.html',username=user,productos=resultados, error = error)
        return render_template('index.html', productos=resultados, error = error)
    else:
        return render_template('index.html', productos=None)

@app.route("/cuenta", methods=['GET','POST'])
def cuenta():
    if 'username' in session:
        user = session['username']
        return render_template('cuenta.html',username=user)
    return render_template('cuenta.html')

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
            if request.form['boton'] == 'pedido':
                fecha = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                dict_usuarios[email]['pedidos'][len(dict_usuarios[email]['pedidos'])]={'productos':dict_usuarios[email]['carrito'],'fecha':fecha}
                dict_usuarios[email]['carrito']=[]
                with open('static/data/usuarios.json', 'w') as fp:
                    json.dump(dict_usuarios, fp)
                carrito, pedido = consultarCarrito(email)
                return render_template('cart.html',username=user,carrito=carrito, error="Pedido realizado exitosamente.", pedido=pedido)
            else:
                producto = request.form['boton']
                dict_usuarios[email]['carrito'].remove(producto)
                with open('static/data/usuarios.json', 'w') as fp:
                    json.dump(dict_usuarios, fp)
                carrito, pedido = consultarCarrito(email)
                return render_template('cart.html',username=user,carrito=carrito, error="Producto eliminado del carrito.", pedido=pedido)
        else:
            carrito, pedido = consultarCarrito(email)
            if pedido:
                return render_template('cart.html',username=user,carrito=carrito, pedido=pedido)
            return render_template('cart.html',username=user,error="Tu carrito está vacío",carrito=carrito,pedido=pedido)

    else:
        return render_template('cart.html', carrito=None, error="Inicia sesión primero.")

@app.route('/pedidos',methods=['GET','POST'])
def pedidos():
    if 'username' in session:
        user = session['username']
        email = session['email']
        if request.method == 'POST':
            pedido = request.form['boton']
            llaves = list(dict_usuarios[email]['pedidos'].keys())
            lista_pedidos = [x for x in list(dict_usuarios[email]['pedidos'].keys()) if str(x) != str(pedido)]
            pedidos_usuario={k:v for k,v in dict_usuarios[email]['pedidos'].items()}
            dict_usuarios[email]['pedidos']= {k:v for k,v in pedidos_usuario.items() if k in lista_pedidos}
            #print(dict_usuarios, pedido, lista_pedidos, llaves, pedidos_usuario)
            with open('static/data/usuarios.json', 'w') as fp:
                json.dump(dict_usuarios, fp)
            pedidos=consultarPedidos(email)
            return render_template('pedidos.html', username=user, pedidos=pedidos, error='Pedido cancelado exitosamente.')
        else:
            pedidos = consultarPedidos(email)
            if (len(pedidos.keys())>0):
                return render_template('pedidos.html', username=user, pedidos=pedidos)
            return render_template('pedidos.html', username=user, pedidos=pedidos, error='No has realizado ningún pedido.')
    else:
        return render_template('pedidos.html', error="Inicia sesión primero.")


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
        dict_usuarios[email]['pedidos'] = {}
        dict_usuarios[email]['admin'] = False
        with open('static/data/usuarios.json', 'w') as fp:
                json.dump(dict_usuarios, fp)
        session['username'] = name
        session['email'] = email
        return redirect('/')
    return render_template('registro.html')

def consultarCarrito(email):
    carrito={'productos':{}, 'total':0}
    for k,v in dict_productos.items():
        if k in dict_usuarios[email]['carrito']:
            carrito['productos'][k]=v
            carrito['productos'][k]['cantidad']=dict_usuarios[email]['carrito'].count(k)
            carrito['total']+=dict_productos[k]['precio']*carrito['productos'][k]['cantidad']
    pedido=(len(carrito['productos'].keys()) > 0)
    return carrito, pedido

def consultarPedidos(email):
    with open('static/data/usuarios.json') as f:
        dict_usuarios = json.load(f)
    pedidos={}
    for k in dict_usuarios[email]['pedidos'].keys():
        pedidos[k]={'productos':{}, 'total':0}
        for k2,v2 in dict_productos.items():
            if k2 in dict_usuarios[email]['pedidos'][k]['productos']:
                pedidos[k]['productos'][k2]=v2
                cantidad = dict_usuarios[email]['pedidos'][k]['productos'].count(k2)
                pedidos[k]['productos'][k2]['cantidad']= cantidad
                pedidos[k]['total']+= dict_productos[k2]['precio']*cantidad
                pedidos[k]['fecha']=dict_usuarios[email]['pedidos'][k]['fecha']
    return pedidos

if __name__ == '__main__':
    app.run(debug=True)