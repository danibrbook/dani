from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "dc7075624f3c41c783f4666041277e33"

# Configuração do banco de dados
def init_db():
    conn = sqlite3.connect('brbook.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            curtidas INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            lida INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Rota: Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        conn = sqlite3.connect('brbook.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE nome = ? AND senha = ?', (nome, senha))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['usuario'] = nome
            return redirect(url_for('feed'))
        else:
            return render_template('index.html', erro="Usuário ou senha inválidos.")
    return render_template('index.html')

# Rota: Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        conn = sqlite3.connect('brbook.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO usuarios (nome, senha) VALUES (?, ?)', (nome, senha))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', erro="Usuário já existe.")
    return render_template('register.html')

# Rota: Feed
@app.route('/feed', methods=['GET', 'POST'])
def feed():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('brbook.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        conteudo = request.form['conteudo']
        cursor.execute('INSERT INTO posts (usuario, conteudo) VALUES (?, ?)', (session['usuario'], conteudo))
        conn.commit()
    
    cursor.execute('SELECT * FROM posts ORDER BY id DESC')
    posts = cursor.fetchall()
    conn.close()
    
    return render_template('feed.html', usuario=session['usuario'], posts=posts)

# Rota: Notícias
@app.route('/noticias')
def noticias():
    api_key = "dc7075624f3c41c783f4666041277e33"  # Substitua pela sua chave da News API
    url = f"https://newsapi.org/v2/top-headlines?country=br&apiKey={api_key}"
    response = requests.get(url)
    noticias = response.json().get("articles", []) if response.status_code == 200 else []
    return render_template('noticias.html', noticias=noticias)

# Rota: Notificações
@app.route('/notificacoes')
def notificacoes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('brbook.db')
    cursor = conn.cursor()
    cursor.execute('SELECT mensagem FROM notificacoes WHERE usuario = ? AND lida = 0', (session['usuario'],))
    notificacoes = cursor.fetchall()
    conn.close()
    
    return render_template('notificacoes.html', notificacoes=notificacoes)

# Rota: Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)