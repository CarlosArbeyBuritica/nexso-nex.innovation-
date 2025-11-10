# app.py
"""
Nexso Next Innovation - Single-file Flask app
- Diseño: negro + dorado
- Audio de bienvenida solo en /
- Admin protegido (usuario: admin / contraseña por defecto: admin123)
- CRUD productos (múltiples imágenes), carrito, checkout, pedidos
- Persistencia en data.json y orders.json
- Carpetas automáticas: static/audio, static/imagenes/Tecnologia, static/imagenes/Diseno
"""

from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, time, uuid

# ---------------- Configuración ----------------
APP_NAME = "Nexso Next Innovation"
BASE_STATIC = "static"
IMG_BASE = os.path.join(BASE_STATIC, "imagenes")
AUDIO_DIR = os.path.join(BASE_STATIC, "audio")
DATA_FILE = "data.json"
ORDERS_FILE = "orders.json"
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_IMAGE = 16 * 1024 * 1024

# Crear carpetas necesarias
os.makedirs(BASE_STATIC, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMG_BASE, exist_ok=True)
for cat in ["Tecnologia", "Diseno"]:
    os.makedirs(os.path.join(IMG_BASE, cat), exist_ok=True)

app = Flask(__name__)
app.secret_key = "cambia_esta_clave_por_otra_muy_segura"  # cámbiala en producción
app.config['MAX_CONTENT_LENGTH'] = MAX_IMAGE

# ---------------- Persistencia ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        default = {
            "site": {
                "titulo": APP_NAME,
                "descripcion": "Innovación y Diseño — Tecnología aplicada a productos únicos.",
                "telefono": "3223007570, 3225466931",
                "cart_button_text": "🛒 Carrito"
            },
            "categories": ["Tecnologia", "Diseno"],
            "products": {},  # pid -> product
            "admin": {
                "username": "admin",
                # contraseña por defecto: admin123
                "password_hash": generate_password_hash("admin123")
            }
        }
        save_data(default)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_order(o):
    orders = load_orders()
    orders.append(o)
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

DATA = load_data()

# ---------------- Utilidades ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def now_ts():
    return int(time.time())

def product_list():
    return list(DATA.get("products", {}).values())

def get_product(pid):
    return DATA.get("products", {}).get(pid)

def save_uploaded_image(file_storage, category):
    filename_raw = secure_filename(file_storage.filename)
    timestamp = str(int(time.time()))
    uid = uuid.uuid4().hex[:6]
    filename = f"{timestamp}_{uid}_{filename_raw}"
    cat_dir = os.path.join(IMG_BASE, category)
    os.makedirs(cat_dir, exist_ok=True)
    path = os.path.join(cat_dir, filename)
    file_storage.save(path)
    return filename

# ---------------- Rutas estáticas ----------------
@app.route('/static/imagenes/<categoria>/<filename>')
def serve_image(categoria, filename):
    return send_from_directory(os.path.join(IMG_BASE, categoria), filename)

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

# ---------------- Templates inline (diseño negro + dorado, option B) ----------------
INDEX_HTML = """
<!doctype html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ site.titulo }}</title>
<style>
:root{--gold:#ffd700;--bg:#0b0b0b;--panel:#111;--muted:#ccc}
*{box-sizing:border-box}
body{margin:0;font-family:Inter, system-ui, Arial;background:var(--bg);color:#fff}
header{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;background:linear-gradient(90deg,#0e0e0e,#111)}
.brand{display:flex;gap:12px;align-items:center}
.brand h1{margin:0;color:var(--gold);font-size:1.1rem}
nav a{color:#fff;margin-left:12px;text-decoration:none;font-weight:700}
nav a:hover{color:var(--gold)}
.hero{padding:36px 12px;text-align:center}
.box{max-width:1100px;margin:auto;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));padding:20px;border-radius:12px}
.cta{display:inline-block;padding:10px 16px;border-radius:10px;background:var(--gold);color:#000;font-weight:800;text-decoration:none;margin-top:12px}
.presentation{margin-top:22px;padding:20px;background:var(--panel);border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,0.6)}
.typing{color:var(--gold);font-weight:700}
.grid-cats{display:flex;gap:18px;max-width:1100px;margin:26px auto;justify-content:center;padding:0 12px}
.cat-card{background:#0f0f0f;border-radius:12px;padding:18px;width:320px;cursor:pointer;transition:transform .25s, box-shadow .25s; text-align:left;transform-style:preserve-3d}
.cat-card:hover{transform:translateY(-8px);box-shadow:0 20px 40px rgba(0,0,0,0.6)}
.cat-card h3{color:var(--gold);margin:8px 0}
.preview-thumb{width:100%;height:160px;object-fit:cover;border-radius:8px;display:block}
.footer{padding:20px;text-align:center;color:rgba(255,255,255,0.7)}
#btn-audio{position:fixed;bottom:20px;right:20px;background:var(--gold);color:#000;border:none;border-radius:50%;width:50px;height:50px;cursor:pointer;font-size:20px;box-shadow:0 6px 18px rgba(0,0,0,0.4)}
.cursor{display:inline-block;width:8px;background:var(--gold);margin-left:6px;animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@media(max-width:900px){ .grid-cats{flex-direction:column;align-items:center} .cat-card{width:92%}}
</style>
</head><body>
<header>
  <div class="brand">
    <img src="{{ url_for('static', filename='imagenes/logo.png') }}" alt="logo" style="height:45px;border-radius:8px;">
    <h1>{{ site.titulo }}</h1>
    <div style="font-size:0.9rem;color:rgba(255,255,255,0.7)">{{ site.telefono }}</div>
  </div>

  <nav>
    <a href="{{ url_for('catalog') }}">Catálogo</a>
    <a href="{{ url_for('categoria', nombre='Tecnologia') }}">Tecnologia</a>
    <a href="{{ url_for('categoria', nombre='Diseno') }}">Diseño</a>
    <a href="{{ url_for('cart') }}">{{ site.cart_button_text }}</a>
    <a href="{{ url_for('admin') }}">Admin</a>
  </nav>
</header>

<section class="hero">
  <div class="box">
    <h2>Bienvenido a <strong style="color:var(--gold)">{{ site.titulo }}</strong></h2>
    <p class="presentation">
      <span id="typed" class="typing"></span><span class="cursor"></span>
      <div style="margin-top:12px;color:var(--muted);max-width:900px;margin-left:auto;margin-right:auto">
        {{ site.descripcion }}
      </div>
      <div style="margin-top:14px">
        <a class="cta" href="{{ url_for('catalog') }}">Explorar catálogo</a>
      </div>
    </p>
  </div>
</section>

<section class="grid-cats">
  <div class="cat-card" onclick="location.href='{{ url_for('categoria', nombre='Tecnologia') }}'">
    {% if tech_preview %}
      <img src="{{ tech_preview }}" class="preview-thumb" alt="Tecnologia">
    {% else %}
      <div style="width:100%;height:160px;background:linear-gradient(90deg,#111,#222);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888">Sin imagen</div>
    {% endif %}
    <h3>Tecnologia</h3>
    <p style="color:#ccc">Productos innovadores, gadgets y soluciones tecnológicas.</p>
  </div>

  <div class="cat-card" onclick="location.href='{{ url_for('categoria', nombre='Diseno') }}'">
    {% if diseno_preview %}
      <img src="{{ diseno_preview }}" class="preview-thumb" alt="Diseno">
    {% else %}
      <div style="width:100%;height:160px;background:linear-gradient(90deg,#111,#222);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888">Sin imagen</div>
    {% endif %}
    <h3>Diseño</h3>
    <p style="color:#ccc">Objetos, decoración y artículos con gran estilo y estética.</p>
  </div>
</section>

<footer class="footer">© {{ year }} {{ site.titulo }}</footer>

<!-- audio welcome (only on home) -->
<audio id="welcome-audio" src="{{ url_for('serve_audio', filename='bienvenida.mp3') }}" preload="auto"></audio>
<button id="btn-audio">🔊</button>


<script>
// typing effect
const txt = "Nos apasiona vender con confianza: calidad, rapidez y atención personalizada para cada cliente.";
let i = 0; const out = document.getElementById('typed');
function typeStep(){
  if(i < txt.length){ out.textContent += txt.charAt(i); i++; setTimeout(typeStep, 28); }
}
window.addEventListener('load', ()=>{ typeStep(); });

// audio play once per session
const audio = document.getElementById('welcome-audio');
const btn = document.getElementById('btn-audio');
window.addEventListener('load', () => {
  if(!sessionStorage.getItem('audioPlayed')) {
    audio.volume = 0.7;
    audio.play().catch(e => console.log('Autoplay bloqueado'));
    sessionStorage.setItem('audioPlayed','1');
  }
});
btn.addEventListener('click', ()=> {
  if(audio.paused) audio.play().catch(()=>{});
  else audio.pause();
  btn.textContent = audio.paused ? '🔇' : '🔊';
});
</script>
</body></html>
"""

# Catalog template (list view)
CATALOG_HTML = """
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Catálogo - {{ site.titulo }}</title>
<style>
:root{--gold:#ffd700;--bg:#0b0b0b}
body{margin:0;font-family:Inter,Arial;background:var(--bg);color:#fff}
header{padding:12px;background:#111;display:flex;align-items:center;justify-content:space-between}
.container{max-width:1200px;margin:18px auto;padding:12px}
.controls{display:flex;gap:8px;align-items:center;margin-bottom:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.card{background:#0f0f0f;padding:12px;border-radius:10px;transition:transform .25s, box-shadow .25s;cursor:pointer;transform-style:preserve-3d}
.card:hover{transform:translateY(-8px) rotateX(3deg) rotateY(1deg);box-shadow:0 20px 40px rgba(0,0,0,0.6)}
.card img{width:100%;height:160px;object-fit:cover;border-radius:8px}
.card h3{color:var(--gold);margin:8px 0}
.price{font-weight:800;color:var(--gold)}
.footer{padding:14px;text-align:center;color:rgba(255,255,255,0.7)}
.btn-new{background:var(--gold);color:#000;padding:8px 12px;border-radius:8px;border:none;cursor:pointer}
</style>
</head><body>
<header>
  <div><a href="{{ url_for('index') }}" style="color:var(--gold);text-decoration:none;font-weight:800">{{ site.titulo }}</a></div>
  <div><a href="{{ url_for('admin') }}">Admin</a></div>
</header>
<div class="container">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2>Catálogo</h2>
    <div><a class="btn-new" href="{{ url_for('crear_producto') }}">+ Nuevo producto</a></div>
  </div>

  <div class="controls">
    <form method="get" action="{{ url_for('catalog') }}" style="display:flex;gap:8px">
      <input name="q" placeholder="Buscar..." value="{{ request.args.get('q','') }}" style="padding:8px;border-radius:8px;border:none">
      <select name="categoria" style="padding:8px;border-radius:8px;border:none">
        <option value="">Todas</option>
        {% for c in categories %}<option value="{{c}}" {% if c==request.args.get('categoria','') %}selected{% endif %}>{{c}}</option>{% endfor %}
      </select>
      <button style="padding:8px;border-radius:8px;border:none;background:var(--gold);font-weight:800">Filtrar</button>
    </form>
  </div>

  <div class="grid">
    {% for p in productos %}
    <div class="card" onclick="location.href='{{ url_for('producto', pid=p.id) }}'">
      {% if p.images and p.images|length>0 %}
        <img src="{{ url_for('serve_image', categoria=p.categoria, filename=p.images[0]) }}" alt="">
      {% else %}
        <div style="width:100%;height:160px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#888">Sin imagen</div>
      {% endif %}
      <h3>{{ p.nombre }}</h3>
      <p style="color:#ddd">{{ p.descripcion[:90] }}{% if p.descripcion|length>90 %}...{% endif %}</p>
      <div class="price">${{ p.precio }}</div>
    </div>
    {% endfor %}
  </div>

</div>
<footer class="footer">© {{ year }} {{ site.titulo }}</footer>
</body></html>
"""

PRODUCT_HTML = """
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ p.nombre }} - {{ site.titulo }}</title>
<style>
body{margin:0;font-family:Inter,Arial;background:#0b0b0b;color:#fff}
.wrap{max-width:1000px;margin:18px auto;padding:12px}
.gallery{display:flex;gap:12px;flex-wrap:wrap}
.gallery img{width:calc(33% - 8px);border-radius:8px;object-fit:cover}
@media(max-width:800px){ .gallery img{width:100%} }
.price{font-weight:900;color:#ffd700;font-size:1.4rem;margin-top:8px}
.btn{background:#ffd700;border:none;padding:10px 14px;border-radius:8px;font-weight:800;cursor:pointer}
</style>
</head><body>
<div class="wrap">
  <a href="{{ url_for('catalog') }}" style="color:rgba(255,255,255,0.7)">← Volver al catálogo</a>
  <h1 style="color:#ffd700">{{ p.nombre }}</h1>
  <div class="price">${{ p.precio }}</div>
  <p style="color:#ddd">{{ p.descripcion }}</p>

  <div class="gallery">
    {% for img in p.images %}
      <img src="{{ url_for('serve_image', categoria=p.categoria, filename=img) }}" alt="">
    {% endfor %}
  </div>

  <form method="POST" action="{{ url_for('add_to_cart', pid=p.id) }}">
    <label>Cantidad: <input type="number" name="cantidad" value="1" min="1" style="width:80px;padding:6px;border-radius:6px;margin-left:8px"></label>
    <button class="btn" style="margin-left:12px">Agregar al carrito</button>
  </form>

  <div style="margin-top:18px">
    <a class="btn" href="{{ url_for('editar_producto', pid=p.id) }}">Editar producto (Admin)</a>
  </div>
</div>
</body></html>
"""

ADMIN_LOGIN_HTML = """
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin - {{ site.titulo }}</title>
<style>body{background:#0b0b0b;color:#fff;font-family:Inter,Arial;display:flex;align-items:center;justify-content:center;height:100vh}.box{background:#111;padding:20px;border-radius:10px;width:360px} input{width:100%;padding:8px;border-radius:6px;border:none;margin-top:8px}</style></head><body>
<div class="box">
  <h2 style="color:#ffd700">Acceso administrador</h2>
  {% if error %}<div style="color:#f66">{{ error }}</div>{% endif %}
  <form method="POST">
    <input name="username" placeholder="Usuario"><br>
    <input name="password" placeholder="Contraseña" type="password"><br>
    <button style="background:#ffd700;border:none;padding:10px;border-radius:8px;margin-top:10px;font-weight:800">Entrar</button>
  </form>
  <p style="color:#888;margin-top:10px">Usuario por defecto: <b>admin</b> / Contraseña: <b>admin123</b></p>
  <p style="margin-top:8px"><a href='{{ url_for(\"index\") }}' style="color:#fff">Volver al sitio</a></p>
</div>
</body></html>
"""

ADMIN_PANEL_HTML = """
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin - {{ site.titulo }}</title>
<style>body{background:#070707;color:#fff;font-family:Inter,Arial;padding:12px}.wrap{max-width:1100px;margin:auto}.section{background:#0f0f0f;padding:12px;border-radius:10px;margin-top:12px} input,textarea,select{width:100%;padding:8px;border-radius:8px;background:transparent;border:1px solid rgba(255,255,255,0.06);color:#fff} img{width:80px;border-radius:6px}</style></head><body>
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="color:#ffd700">Panel de Administración</h2><div><a href="{{ url_for('index') }}" style="color:#fff;margin-right:8px">Ver sitio</a><a href="{{ url_for('logout') }}" style="color:#f66">Salir</a></div></div>

  <div class="section">
    <h3>Crear producto</h3>
    <form method="POST" action="{{ url_for('crear_producto') }}" enctype="multipart/form-data">
      <label>Nombre</label><input name="nombre" required>
      <label>Precio</label><input name="precio" required>
      <label>Categoría</label>
      <select name="categoria">{% for c in categories %}<option value="{{ c }}">{{ c }}</option>{% endfor %}</select>
      <label>Descripción</label><textarea name="descripcion"></textarea>
      <label>Imágenes (puedes seleccionar varias)</label><input type="file" name="imagenes" multiple accept="image/*">
      <div style="margin-top:8px"><button style="background:#ffd700;border:none;padding:10px;border-radius:8px;font-weight:800">Crear producto</button></div>
    </form>
  </div>

  <div class="section">
    <h3>Productos existentes</h3>
    <table style="width:100%;border-collapse:collapse"><thead><tr><th>Imagen</th><th>Nombre</th><th>Precio</th><th>Categoria</th><th>Acciones</th></tr></thead><tbody>
    {% for p in productos %}
      <tr>
        <td>{% if p.images and p.images|length>0 %}<img src="{{ url_for('serve_image', categoria=p.categoria, filename=p.images[0]) }}">{% else %}Sin img{% endif %}</td>
        <td>{{ p.nombre }}</td>
        <td>${{ p.precio }}</td>
        <td>{{ p.categoria }}</td>
        <td>
          <a href="{{ url_for('editar_producto', pid=p.id) }}" style="color:var(--gold)">Editar</a> |
          <form method="POST" action="{{ url_for('eliminar_producto', pid=p.id) }}" style="display:inline" onsubmit="return confirm('Eliminar producto?');"><button style="background:#f66;border:none;color:#fff;padding:6px 8px;border-radius:6px">Eliminar</button></form>
        </td>
      </tr>
    {% endfor %}
    </tbody></table>
  </div>

  <div class="section">
    <h3>Categorías</h3>
    <form method="POST" action="{{ url_for('guardar_categorias') }}">
      <label>Lista de categorías (separadas por coma)</label><input name="cats" value="{{ ', '.join(categories) }}">
      <div style="margin-top:8px"><button style="background:#ffd700;border:none;padding:8px;border-radius:8px">Guardar categorías</button></div>
    </form>
  </div>

  <div class="section">
    <h3>Pedidos</h3>
    <p><a style="color:#ffd700" href="{{ url_for('ver_pedidos') }}">Ver pedidos</a></p>
  </div>
</div>
</body></html>
"""

EDIT_PRODUCT_HTML = """
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Editar - {{ p.nombre }}</title>
<style>body{background:#0b0b0b;color:#fff;font-family:Inter,Arial;padding:12px}.wrap{max-width:900px;margin:auto} input,textarea,select{width:100%;padding:8px;border-radius:8px;border:none;background:#111;color:#fff} img{width:120px;border-radius:8px;margin-right:8px}</style></head><body>
<div class="wrap">
  <h2 style="color:#ffd700">Editar producto</h2>
  <form method="POST" enctype="multipart/form-data">
    <label>Nombre</label><input name="nombre" value="{{ p.nombre }}">
    <label>Precio</label><input name="precio" value="{{ p.precio }}">
    <label>Categoria</label><select name="categoria">{% for c in categories %}<option value="{{ c }}" {% if c==p.categoria %}selected{% endif %}>{{ c }}</option>{% endfor %}</select>
    <label>Descripcion</label><textarea name="descripcion">{{ p.descripcion }}</textarea>
    <label>Subir nuevas imágenes (opcional)</label><input type="file" name="imagenes" multiple accept="image/*">
    <div style="margin-top:12px"><button style="background:#ffd700;border:none;padding:10px;border-radius:8px">Guardar</button></div>
  </form>

  <h3 style="margin-top:18px">Imágenes actuales</h3>
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    {% for img in p.images %}
      <div style="text-align:center">
        <img src="{{ url_for('serve_image', categoria=p.categoria, filename=img) }}"><br>
        <form method="POST" action="{{ url_for('eliminar_imagen', pid=p.id, filename=img) }}" onsubmit="return confirm('Eliminar esta imagen?');">
          <button style="background:#f66;border:none;color:#fff;padding:6px 8px;border-radius:6px;margin-top:6px">Eliminar</button>
        </form>
      </div>
    {% endfor %}
  </div>
</div>
</body></html>
"""

ORDERS_HTML = """
<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pedidos - {{ site.titulo }}</title>
<style>body{background:#070707;color:#fff;font-family:Inter,Arial;padding:12px}.wrap{max-width:1000px;margin:auto}.order{background:#0f0f0f;padding:12px;border-radius:8px;margin-bottom:10px}</style></head><body>
<div class="wrap">
  <h2 style="color:#ffd700">Pedidos registrados</h2>
  <p><a href="{{ url_for('admin') }}" style="color:#fff">← Volver al admin</a></p>
  {% for o in orders %}
    <div class="order">
      <div><strong>ID:</strong> {{ o.id }} — <small>{{ o.time }}</small></div>
      <div><strong>Cliente:</strong> {{ o.cliente.nombre }} — {{ o.cliente.telefono }}</div>
      <div><strong>Dirección:</strong> {{ o.cliente.direccion }}</div>
      <div><strong>Total:</strong> ${{ "%.2f"|format(o.total) }}</div>
      <div><strong>Items:</strong>
        <ul>{% for it in o.items %}<li>{{ it.qty }} × {{ it.product.nombre }} — ${{ "%.2f"|format(it.subtotal) }}</li>{% endfor %}</ul>
      </div>
    </div>
  {% else %}
    <p>No hay pedidos.</p>
  {% endfor %}
</div>
</body></html>
"""

# ---------------- Rutas públicas ----------------
@app.route('/')
def index():
    tech_preview = None
    diseno_preview = None
    for p in product_list():
        if p['categoria'] == "Tecnologia" and not tech_preview and p.get('images'):
            tech_preview = url_for('serve_image', categoria="Tecnologia", filename=p['images'][0])
        if p['categoria'] == "Diseno" and not diseno_preview and p.get('images'):
            diseno_preview = url_for('serve_image', categoria="Diseno", filename=p['images'][0])
    return render_template_string(INDEX_HTML, site=DATA['site'], tech_preview=tech_preview, diseno_preview=diseno_preview, year=time.localtime().tm_year)

@app.route('/catalog')
def catalog():
    q = request.args.get('q','').strip().lower()
    cat = request.args.get('categoria','')
    productos = product_list()
    if q:
        productos = [p for p in productos if q in (p['nombre'].lower() + p['descripcion'].lower())]
    if cat:
        productos = [p for p in productos if p['categoria'] == cat]
    return render_template_string(CATALOG_HTML, productos=productos, site=DATA['site'], categories=DATA.get('categories', ["Tecnologia","Diseno"]), year=time.localtime().tm_year, request=request)

@app.route('/categoria/<nombre>')
def categoria(nombre):
    folder = os.path.join(IMG_BASE, nombre)
    if not os.path.exists(folder):
        return "Categoría no encontrada", 404
    productos = [p for p in product_list() if p['categoria'] == nombre]
    imgs = [f for f in os.listdir(folder) if f.lower().endswith(tuple(ALLOWED_EXT))]
    # render custom category view (simple)
    return render_template_string("""
    <!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{{ nombre }} - {{ site.titulo }}</title>
    <style>:root{--gold:#ffd700}body{margin:0;font-family:Inter,Arial;background:#0b0b0b;color:#fff}header{padding:12px;background:#111;display:flex;justify-content:space-between} .wrap{max-width:1100px;margin:18px auto;padding:12px}.titulo{color:var(--gold);margin-bottom:6px}.desc{color:#ccc;margin-bottom:12px}.gal{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.gal img{width:100%;height:160px;object-fit:cover;border-radius:8px;transition:transform .25s}.gal img:hover{transform:scale(1.05) rotateX(3deg)}.prod{background:#0f0f0f;padding:12px;border-radius:10px;margin-top:18px}</style></head><body>
    <header><a href='{{ url_for(\"index\") }}' style='color:var(--gold);text-decoration:none;font-weight:800'>{{ site.titulo }}</a><div><a href='{{ url_for(\"catalog\") }}' style='color:#fff'>Catálogo</a></div></header>
    <div class='wrap'>
      <h2 class='titulo'>{{ nombre }}</h2>
      {% if nombre == 'Tecnologia' %}
        <p class='desc'>Variedad de gadgets, accesorios y soluciones tecnológicas.</p>
      {% else %}
        <p class='desc'>Artículos de diseño y decoración con estilo.</p>
      {% endif %}
      <div class='gal'>
        {% for im in imgs %}
          <img src='{{ url_for(\"serve_image\", categoria=nombre, filename=im) }}'>
        {% else %}
          <div style="color:#888">No hay imágenes en la galería</div>
        {% endfor %}
      </div>

      <div class='prod'>
        <h3 style='color:var(--gold)'>Productos en {{ nombre }}</h3>
        {% for p in productos %}
          <div style='background:#111;padding:10px;border-radius:8px;margin-bottom:8px'>
            <strong style='color:var(--gold)'>{{ p.nombre }}</strong> — ${{ p.precio }}<br>
            <small style='color:#ccc'>{{ p.descripcion[:120] }}{% if p.descripcion|length>120 %}...{% endif %}</small><br>
            <a href='{{ url_for(\"producto\", pid=p.id) }}' style='color:var(--gold)'>Ver producto</a>
          </div>
        {% else %}
          <p style='color:#888'>No hay productos en esta categoría.</p>
        {% endfor %}
      </div>
    </div></body></html>
    """, nombre=nombre, imgs=imgs, productos=productos, site=DATA['site'])

@app.route('/producto/<pid>')
def producto(pid):
    p = get_product(pid)
    if not p: return "Producto no encontrado", 404
    return render_template_string(PRODUCT_HTML, p=p, site=DATA['site'])

# ---------------- Carrito ----------------
@app.route('/add_to_cart/<pid>', methods=['POST'])
def add_to_cart(pid):
    qty = int(request.form.get('cantidad', 1))
    cart = session.get('cart', {})
    cart[pid] = cart.get(pid, 0) + qty
    session['cart'] = cart
    flash("Añadido al carrito")
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0.0
    for pid, qty in cart.items():
        p = get_product(pid)
        if not p: continue
        price = float(str(p['precio']).replace(',',''))
        subtotal = price * qty
        items.append({'product':p, 'qty':qty, 'subtotal':subtotal})
        total += subtotal
    # simple template
    html = "<h2 style='color:#ffd700'>Carrito</h2>"
    if not items:
        html += "<p>Tu carrito está vacío. <a href='/catalog'>Ir al catálogo</a></p>"
    else:
        html += "<ul>"
        for it in items:
            html += f"<li>{it['qty']} × {it['product']['nombre']} — ${it['subtotal']:.2f}</li>"
        html += "</ul>"
        html += f"<p><strong>Total: ${total:.2f}</strong></p>"
        html += "<p><a href='/checkout' style='background:#ffd700;color:#000;padding:8px;border-radius:8px;text-decoration:none'>Proceder al pago</a></p>"
    return html

@app.route('/checkout', methods=['GET','POST'])
def checkout():
    cart = session.get('cart', {})
    items = []
    total = 0.0
    for pid, qty in cart.items():
        p = get_product(pid)
        if not p: continue
        price = float(str(p['precio']).replace(',',''))
        subtotal = price * qty
        items.append({'product':p, 'qty':qty, 'subtotal':subtotal})
        total += subtotal
    if request.method == 'POST':
        nombre = request.form.get('nombre','Cliente')
        telefono = request.form.get('telefono','')
        direccion = request.form.get('direccion','')
        pedido = {
            "id": str(uuid.uuid4()),
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_ts())),
            "cliente": {"nombre": nombre, "telefono": telefono, "direccion": direccion},
            "items": items,
            "total": total
        }
        save_order(pedido)
        session['cart'] = {}
        return f"<h2>Gracias {nombre}, pedido registrado ({pedido['id']}) — Total: ${total:.2f}</h2><p><a href='/'>Volver</a></p>"
    # form
    return """
    <h2 style='color:#ffd700'>Checkout</h2>
    <form method='POST'>
      <label>Nombre:<br><input name='nombre' required style='padding:8px;border-radius:6px'></label><br><br>
      <label>Teléfono:<br><input name='telefono' style='padding:8px;border-radius:6px'></label><br><br>
      <label>Dirección:<br><textarea name='direccion' style='padding:8px;border-radius:6px'></textarea></label><br><br>
      <button style='background:#ffd700;color:#000;padding:10px;border-radius:8px;border:none'>Confirmar pedido</button>
    </form>
    """

# ---------------- Admin ----------------
@app.route('/admin', methods=['GET','POST'])
def admin():
    if 'admin_user' not in session:
        error = None
        if request.method == 'POST':
            username = request.form.get('username','')
            password = request.form.get('password','')
            admin_conf = DATA.get('admin', {})
            if username == admin_conf.get('username') and check_password_hash(admin_conf.get('password_hash',''), password):
                session['admin_user'] = username
                return redirect(url_for('admin'))
            else:
                error = "Usuario o contraseña incorrectos"
        return render_template_string(ADMIN_LOGIN_HTML, site=DATA['site'], error=error)
    productos = product_list()
    return render_template_string(ADMIN_PANEL_HTML, site=DATA['site'], productos=productos, categories=DATA.get('categories', ["Tecnologia","Diseno"]))

@app.route('/logout')
def logout():
    session.pop('admin_user', None)
    return redirect(url_for('index'))

@app.route('/crear_producto', methods=['GET','POST'])
def crear_producto():
    if 'admin_user' not in session:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        nombre = request.form.get('nombre','Producto')
        precio = request.form.get('precio','0')
        categoria = request.form.get('categoria', DATA.get('categories',[ "Tecnologia" ])[0])
        descripcion = request.form.get('descripcion','')
        pid = str(uuid.uuid4())
        images = []
        files = request.files.getlist('imagenes')
        for f in files:
            if f and allowed_file(f.filename):
                fn = save_uploaded_image(f, categoria)
                images.append(fn)
        prod = {"id":pid, "nombre":nombre, "precio":precio, "categoria":categoria, "descripcion":descripcion, "images":images, "created": now_ts()}
        DATA.setdefault('products', {})[pid] = prod
        save_data(DATA)
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))

@app.route('/editar_producto/<pid>', methods=['GET','POST'])
def editar_producto(pid):
    if 'admin_user' not in session:
        return redirect(url_for('admin'))
    p = get_product(pid)
    if not p: return "No encontrado", 404
    if request.method == 'POST':
        p['nombre'] = request.form.get('nombre', p['nombre'])
        p['precio'] = request.form.get('precio', p['precio'])
        new_cat = request.form.get('categoria', p['categoria'])
        if new_cat and new_cat not in DATA.get('categories', []):
            DATA.setdefault('categories', []).append(new_cat)
            os.makedirs(os.path.join(IMG_BASE, new_cat), exist_ok=True)
        # if category changed, move images
        if new_cat != p['categoria']:
            old_dir = os.path.join(IMG_BASE, p['categoria'])
            new_dir = os.path.join(IMG_BASE, new_cat)
            os.makedirs(new_dir, exist_ok=True)
            for img in list(p.get('images', [])):
                old_path = os.path.join(old_dir, img)
                new_path = os.path.join(new_dir, img)
                try:
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                except:
                    pass
            p['categoria'] = new_cat
        p['descripcion'] = request.form.get('descripcion', p['descripcion'])
        files = request.files.getlist('imagenes')
        for f in files:
            if f and allowed_file(f.filename):
                fn = save_uploaded_image(f, p['categoria'])
                p['images'].append(fn)
        save_data(DATA)
        return redirect(url_for('admin'))
    return render_template_string(EDIT_PRODUCT_HTML, p=p, categories=DATA.get('categories', ["Tecnologia","Diseno"]))

@app.route('/eliminar_producto/<pid>', methods=['POST'])
def eliminar_producto(pid):
    if 'admin_user' not in session:
        return redirect(url_for('admin'))
    p = get_product(pid)
    if not p:
        return redirect(url_for('admin'))
    for im in p.get('images', []):
        path = os.path.join(IMG_BASE, p['categoria'], im)
        try:
            if os.path.exists(path): os.remove(path)
        except:
            pass
    DATA['products'].pop(pid, None)
    save_data(DATA)
    return redirect(url_for('admin'))

@app.route('/eliminar_imagen/<pid>/<filename>', methods=['POST'])
def eliminar_imagen(pid, filename):
    if 'admin_user' not in session:
        return redirect(url_for('admin'))
    p = get_product(pid)
    if not p:
        return redirect(url_for('admin'))
    if filename in p.get('images', []):
        try:
            os.remove(os.path.join(IMG_BASE, p['categoria'], filename))
        except:
            pass
        p['images'].remove(filename)
        save_data(DATA)
    return redirect(url_for('editar_producto', pid=pid))

@app.route('/guardar_categorias', methods=['POST'])
def guardar_categorias():
    if 'admin_user' not in session:
        return redirect(url_for('admin'))
    raw = request.form.get('cats','')
    cats = [c.strip() for c in raw.split(',') if c.strip()]
    DATA['categories'] = cats
    for c in cats:
        os.makedirs(os.path.join(IMG_BASE, c), exist_ok=True)
    save_data(DATA)
    return redirect(url_for('admin'))

@app.route('/ver_pedidos')
def ver_pedidos():
    if 'admin_user' not in session:
        return redirect(url_for('admin'))
    orders = load_orders()
    return render_template_string(ORDERS_HTML, orders=orders, site=DATA['site'])

# API
@app.route('/api/products')
def api_products():
    return jsonify(product_list())

# ---------------- Sincronizar imágenes sueltas a productos si hay archivos existentes ----------------
def sync_from_existing_images():
    changed = False
    DATA.setdefault('products', {})
    for cat in DATA.get('categories', ["Tecnologia","Diseno"]):
        folder = os.path.join(IMG_BASE, cat)
        if not os.path.exists(folder): continue
        for fname in os.listdir(folder):
            if not allowed_file(fname): continue
            found = False
            for p in DATA['products'].values():
                if fname in p.get('images', []) and p.get('categoria') == cat:
                    found = True; break
            if not found:
                pid = str(uuid.uuid4())
                DATA['products'][pid] = {
                    "id": pid,
                    "nombre": os.path.splitext(fname)[0].replace('_',' ').title(),
                    "precio": "1200",
                    "categoria": cat,
                    "descripcion": "Descripción pendiente...",
                    "images": [fname],
                    "created": now_ts()
                }
                changed = True
    if changed:
        save_data(DATA)

sync_from_existing_images()

# ---------------- Ejecutar ----------------
if __name__ == '__main__':
    print("🚀 Ejecutando Nexso Next Innovation en http://127.0.0.1:5000")
    print("Admin usuario: admin  contraseña por defecto: admin123  (cámbiala desde el panel)")
    app.run(debug=True, host='0.0.0.0', port=5000)
