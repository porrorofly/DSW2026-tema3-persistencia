# Archivo: app/main.py
import os
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, url_for
from app.models import db, Producto
from app.forms import ProductoForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"

# Configuración de la base de datos SQLite local
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tienda.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Configurar la carpeta destino para las imágenes
app.config["UPLOAD_FOLDER"] = os.path.join("app", "static", "img", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 # Límite de 2MB por seguridad

db.init_app(app)

with app.app_context():
    db.create_all()

    if not Producto.query.first():
        nuevo_producto = Producto(
            nombre="Teclado Mecánico RGB", precio=49.99, disponible=True
        )
        db.session.add(nuevo_producto)
        db.session.commit()


@app.route("/")
def home():
    # Redirigimos la raíz directamente al catálogo
    return redirect(url_for("mostrar_catalogo"))


# 1. READ: Mostrar todos los productos en la plantilla catalogo.html
@app.route("/catalogo")
def mostrar_catalogo():
    productos = Producto.query.all()
    return render_template("catalogo.html", lista_productos=productos)


# 2. CREATE: Mostrar formulario y guardar un nuevo producto en la BD
@app.route("/producto/nuevo", methods=["GET", "POST"])
def crear_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        nombre_imagen=None
        
        if form.archivo_imagen.data:
            archivo=form.archivo_imagen.data
            
            #asegurar de que la ruta existe
            os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True)
            nombre_imagen = secure_filename(archivo.filename)
            #Guardar el fichero
            archivo.save(os.path.join(app.config["UPLOAD_FOLDER"],nombre_imagen))

        nuevo_prod = Producto(
            nombre=form.nombre.data,
            precio=form.precio.data,
            disponible=form.disponible.data,
            imagen=nombre_imagen 
        )
        db.session.add(nuevo_prod)
        db.session.commit()
        # Patrón PRG: Redirigimos tras procesar el POST con éxito
        return redirect(url_for("mostrar_catalogo"))

    return render_template("producto_form.html", form=form, titulo="Nuevo Producto")


# 3. UPDATE: Recuperar un producto existente, rellenar el formulario y guardar cambios
@app.route("/producto/<int:prod_id>/editar", methods=["GET", "POST"])
def editar_producto(prod_id):
    # Busca el producto por su clave primaria o lanza un error 404 si no existe
    producto = db.get_or_404(Producto, prod_id)
    
    # Al pasar obj=producto, en la petición GET los campos aparecen ya rellenos con los datos actuales
    form = ProductoForm(obj=producto)
        
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.precio = form.precio.data
        producto.disponible = form.disponible.data
        
        #se actualizan los datos
        if form.archivo_imagen.data:
            archivo=form.archivo_imagen.data
            nombre_imagen=secure_filename(archivo.filename)
            #asegurar de que la ruta existe
            os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True)

            #Guardar el fichero
            print(nombre_imagen)
            archivo.save(os.path.join(app.config["UPLOAD_FOLDER"],nombre_imagen))
            producto.imagen=nombre_imagen 
        # Modificamos directamente los atributos del objeto recuperado de la BD
       
        # Confirmamos los cambios en la BD
        db.session.commit()
        return redirect(url_for("mostrar_catalogo"))

    return render_template("producto_form.html", form=form, titulo="Editar Producto", producto=producto)


# 4. DELETE: Eliminar un producto de la BD (exclusivamente por POST)
@app.route("/producto/<int:prod_id>/eliminar", methods=["POST"])
def eliminar_producto(prod_id):
    producto = db.get_or_404(Producto, prod_id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("mostrar_catalogo"))


if __name__ == "__main__":
    app.run(debug=True)