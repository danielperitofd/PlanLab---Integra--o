import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, abort, flash
from conexao import get_db_connection, create_tables
from functools import wraps

app = Flask(__name__)

app.secret_key = 'chavepararodar'

# Função para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Fecha a conexão após cada solicitação
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Rota para login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = ? and senha = ?', (email, senha))
        
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error="Credenciais inválidas")

    return render_template("login.html")

# Rota para cadastro de login
@app.route("/login_cadastro")
def login_cadastro():
    return render_template('login_cadastro.html')

# Rota para a página inicial
@app.route("/")
@login_required
def index():
    if request.method == "POST":
        # Lógica para processar os dados do formulário
        pass
    else:
        conn = get_db_connection()
        planos = conn.execute("SELECT * FROM aula ORDER BY data_aula DESC LIMIT 4").fetchall()
        conn.close()
        return render_template("index.html", planos=planos)

# Rota para exibir detalhes de uma aula específica
@app.route("/pagina_aula/<int:plano_id>")
@login_required
def pagina_aula(plano_id):
    conn = get_db_connection()
    plano = conn.execute("SELECT * FROM aula WHERE id = ?", (plano_id,)).fetchone()
    conn.close()
    if plano:
        return render_template("pagina_aula.html", plano=plano, plano_id=plano_id)
    else:
        abort(404)

# Rota para editar um plano de aula
@app.route("/editar_plano/<int:plano_id>", methods=["GET", "POST"])
@login_required
def editar_plano(plano_id):
    if request.method == "POST":
        # Verifica se todos os campos necessários estão presentes
        if all(field in request.form for field in ['titulo', 'data_aula', 'turma', 'semestre', 'conteudo_programatico', 'metodologia', 'recursos_necessarios', 'avaliacao_observacoes', 'observacoes', 'eventos_extraordinarios']):
            titulo = request.form.get('titulo')
            data_aula = request.form.get('data_aula')
            turma = request.form.get('turma')
            semestre = request.form.get('semestre')
            conteudo_programatico = request.form.get('conteudo_programatico')
            metodologia = request.form.get('metodologia')
            recursos_necessarios = request.form.get('recursos_necessarios')
            avaliacao_observacoes = request.form.get('avaliacao_observacoes')
            observacoes = request.form.get('observacoes')
            eventos_extraordinarios = request.form.get('eventos_extraordinarios')

            conn = get_db_connection()
            conn.execute("""
                UPDATE aula
                SET titulo = ?, data_aula = ?, turma = ?, semestre = ?, conteudo_programatico = ?, metodologia = ?, 
                    recursos_necessarios = ?, avaliacao_observacoes = ?, observacoes = ?, eventos_extraordinarios = ?
                WHERE id = ?
            """, (titulo, data_aula, turma, semestre, conteudo_programatico, metodologia, recursos_necessarios, avaliacao_observacoes, observacoes, eventos_extraordinarios, plano_id))
            conn.commit()
            conn.close()

            return redirect(url_for("pagina_aula", plano_id=plano_id))
        else:
            # Retorna um erro ou redireciona para uma página de erro, pois algum campo obrigatório está faltando
            flash('Todos os campos são obrigatórios.')
            return redirect(url_for("editar_plano", plano_id=plano_id))
    else:
        conn = get_db_connection()
        plano = conn.execute("SELECT * FROM aula WHERE id = ?", (plano_id,)).fetchone()
        conn.close()
        if not plano:
            abort(404)
        return render_template("editar_plano.html", plano=plano, plano_id=plano_id)

# Rota para o formulário de criação de plano de aula
@app.route("/formulario", methods=['GET', 'POST'])
@login_required
def formulario():
    if request.method == 'POST':
        data_aula
        data_aula = request.form['data_aula']
        turma = request.form['turma']
        semestre = request.form['semestre']
        titulo = request.form['titulo']
        conteudo_programatico = request.form['conteudo_programatico']
        metodologia = request.form['metodologia']
        recursos_necessarios = request.form['recursos_necessarios']
        avaliacao_observacoes = request.form['avaliacao_observacoes']
        observacoes = request.form['observacoes']
        eventos_extraordinarios = request.form['eventos_extraordinarios']
        usuario_id = 1  # Substitua pelo ID do usuário logado
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO aula (data_aula, turma, semestre, titulo, conteudo_programatico, metodologia, recursos_necessarios, avaliacao_observacoes, observacoes, eventos_extraordinarios, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data_aula, turma, semestre, titulo, conteudo_programatico, metodologia, recursos_necessarios, avaliacao_observacoes, observacoes, eventos_extraordinarios, usuario_id))
        conn.commit()
        conn.close()
        return redirect(url_for('planos_de_aula'))
    return render_template('formulario.html')

# Rota para excluir um plano de aula
@app.route("/excluir_plano/<int:plano_id>", methods=["POST"])
@login_required
def excluir_plano(plano_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM aula WHERE id = ?", (plano_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("planos_de_aula"))

# Rota para exibir todos os planos de aula
@app.route("/planos_de_aula")
@login_required
def planos_de_aula():
    conn = get_db_connection()
    planos = conn.execute("SELECT * FROM aula").fetchall()
    conn.close()
    return render_template("planos_de_aula.html", planos=planos)

if __name__ == "__main__":
    app.run(debug=True)
