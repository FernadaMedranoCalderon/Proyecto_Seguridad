from flask import Flask, render_template_string, request
import sqlite3
from seed import USERS, EXPEDIENTES, INJECTION_EXAMPLES, SEARCH_INJECTION_EXAMPLES


app = Flask(__name__)


def init_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE expedientes (
            folio TEXT PRIMARY KEY,
            ciudadano TEXT NOT NULL,
            dependencia TEXT NOT NULL,
            estatus TEXT NOT NULL,
            descripcion TEXT
        )
        """
    )

    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
        USERS,
    )
    cursor.executemany(
        "INSERT INTO expedientes VALUES (?, ?, ?, ?, ?)",
        EXPEDIENTES,
    )
    conn.commit()
    return conn


db_conn = init_db()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Portal Ciudadano - Laboratorio de Injection</title>
    <style>
        :root {
            --bg: #07111f;
            --panel: rgba(10, 18, 31, 0.86);
            --panel-border: rgba(255, 255, 255, 0.08);
            --text: #e8eef8;
            --muted: #9fb0c6;
            --accent: #4dd0e1;
            --accent-2: #7c5cff;
            --danger: #ff7b7b;
            --success: #7dffb2;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, Arial, sans-serif;
            background:
                radial-gradient(circle at top left, rgba(77, 208, 225, 0.22), transparent 32%),
                radial-gradient(circle at bottom right, rgba(124, 92, 255, 0.26), transparent 30%),
                linear-gradient(160deg, #04101c 0%, #091826 45%, #0f1f33 100%);
            color: var(--text);
            min-height: 100vh;
        }

        .shell {
            width: min(1200px, calc(100% - 32px));
            margin: 0 auto;
            padding: 32px 0 48px;
        }

        .hero {
            display: grid;
            grid-template-columns: 1.25fr 0.75fr;
            gap: 20px;
            align-items: stretch;
        }

        .panel {
            background: var(--panel);
            border: 1px solid var(--panel-border);
            border-radius: 24px;
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(18px);
        }

        .headline {
            padding: 28px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 8px 14px;
            border-radius: 999px;
            background: rgba(77, 208, 225, 0.12);
            border: 1px solid rgba(77, 208, 225, 0.26);
            color: var(--accent);
            font-size: 0.88rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        h1 {
            margin: 18px 0 10px;
            font-size: clamp(2rem, 3vw, 3.5rem);
            line-height: 1.03;
        }

        .lede {
            color: var(--muted);
            font-size: 1.02rem;
            max-width: 70ch;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }

        .card {
            padding: 22px;
        }

        .card h2 {
            margin: 0 0 8px;
            font-size: 1.18rem;
        }

        .card p {
            margin: 0 0 16px;
            color: var(--muted);
            line-height: 1.55;
        }

        form {
            display: grid;
            gap: 12px;
        }

        label {
            display: block;
            font-size: 0.92rem;
            color: #ced8e5;
            margin-bottom: 6px;
        }

        input {
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.05);
            color: var(--text);
            border-radius: 14px;
            padding: 14px 16px;
            outline: none;
        }

        input:focus {
            border-color: rgba(77, 208, 225, 0.75);
            box-shadow: 0 0 0 4px rgba(77, 208, 225, 0.12);
        }

        button {
            border: 0;
            border-radius: 14px;
            padding: 14px 16px;
            font-weight: 700;
            color: #03111a;
            background: linear-gradient(135deg, var(--accent), #9ff7ff);
            cursor: pointer;
        }

        .meta {
            display: grid;
            gap: 12px;
        }

        .stat {
            padding: 18px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stat strong {
            display: block;
            margin-bottom: 6px;
            color: var(--accent);
        }

        .messages {
            margin-top: 20px;
            display: grid;
            gap: 12px;
        }

        .message {
            padding: 14px 16px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.04);
        }

        .message.error { color: var(--danger); }
        .message.success { color: var(--success); }
        .message.info { color: var(--accent); }

        .results {
            display: grid;
            gap: 10px;
            margin-top: 14px;
        }

        .row {
            display: flex;
            justify-content: space-between;
            gap: 14px;
            padding: 14px 16px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .row span {
            color: var(--muted);
        }

        .sql-box {
            margin-top: 16px;
            padding: 14px 16px;
            border-radius: 14px;
            background: rgba(0, 0, 0, 0.32);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #cfe9ff;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .footer-note {
            margin-top: 16px;
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.6;
        }

        @media (max-width: 900px) {
            .hero, .grid { grid-template-columns: 1fr; }
        }

        .injection-list {
            display: grid;
            gap: 10px;
        }

        .injection-item {
            padding: 14px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 107, 107, 0.3);
        }

        .injection-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .copy-btn {
            padding: 6px 12px;
            background: rgba(77, 208, 225, 0.2);
            border: 1px solid rgba(77, 208, 225, 0.5);
            color: var(--accent);
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .copy-btn:hover {
            background: rgba(77, 208, 225, 0.4);
        }

        .injection-detail {
            font-size: 0.9rem;
            display: grid;
            gap: 6px;
        }

        code {
            background: rgba(0, 0, 0, 0.4);
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            color: #ffff99;
            word-break: break-all;
        }

        h3 {
            margin: 0 0 12px;
            font-size: 1rem;
        }

        .users-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 0.9rem;
        }

        .users-table th, .users-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .users-table th {
            background: rgba(77, 208, 225, 0.1);
            color: var(--accent);
            font-weight: 600;
        }

        .users-table tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <div class="panel headline">
                <div class="eyebrow">A05:2025 Injection - laboratorio falso</div>
                <h1>Portal Ciudadano de Expedientes</h1>
                <p class="lede">
                    Esta pagina simula un sistema gubernamental de consulta con datos ficticios para una
                    demostracion tecnica. En la rama <strong>main</strong> la construccion de consultas es
                    deliberadamente insegura para mostrar el impacto de una inyeccion SQL en un entorno controlado.
                </p>
                <div class="messages">
                    {% if error %}<div class="message error">{{ error }}</div>{% endif %}
                    {% if success %}<div class="message success">{{ success }}</div>{% endif %}
                    {% if info %}<div class="message info">{{ info }}</div>{% endif %}
                </div>
            </div>

            <aside class="panel card meta">
                <div class="stat">
                    <strong>Datos</strong>
                    Expedientes, usuarios y estados completamente simulados.
                </div>
                <div class="stat">
                    <strong>Alcance</strong>
                    Diseñado para divulgacion tecnica en una red local o laboratorio aislado.
                </div>
                <div class="stat">
                    <strong>Objetivo</strong>
                    Mostrar como una concatenacion de cadenas termina comprometiendo el control de acceso.
                </div>

                <div style="margin-top: 20px;">
                    <h3 style="color: var(--accent);">Usuarios en la BD</h3>
                    <table class="users-table">
                        <thead>
                            <tr>
                                <th>Usuario</th>
                                <th>Contraseña</th>
                                <th>Rol</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for user in users %}
                            <tr>
                                <td>{{ user.username }}</td>
                                <td><code>{{ user.password }}</code></td>
                                <td>{{ user.role }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </aside>
        </section>

        <section class="grid">
            <article class="panel card">
                <h2>Acceso al portal</h2>
                <p>Formulario de autenticacion con una implementacion vulnerable para la version principal.</p>
                <form method="post" id="loginForm">
                    <input type="hidden" name="action" value="login">
                    <div>
                        <label for="username">Usuario</label>
                        <input id="username" type="text" name="username" placeholder="admin" required>
                    </div>
                    <div>
                        <label for="password">Clave</label>
                        <input id="password" type="password" name="password" placeholder="password123" required>
                    </div>
                    <button type="submit">Entrar</button>
                </form>

                <div style="margin-top: 20px;">
                    <h3 style="color: var(--accent); margin-bottom: 12px;">Ejemplos de inyecciones para el login</h3>
                    <div class="injection-list">
                        {% for example in injection_examples %}
                        <div class="injection-item">
                            <div class="injection-header">
                                <strong>{{ example.name }}</strong>
                                <button type="button" class="copy-btn" onclick="fillLogin('{{ example.user|replace("'", "\\'") }}', '{{ example.pass|replace("'", "\\'") }}')">Usar</button>
                            </div>
                            <div class="injection-detail">
                                <div><small style="color: var(--muted);">Usuario:</small> <code>{{ example.user }}</code></div>
                                <div><small style="color: var(--muted);">Contraseña:</small> <code>{{ example.pass }}</code></div>
                                <div style="margin-top: 8px; color: #a0b0c0; font-size: 0.9rem;">{{ example.description }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </article>

            <article class="panel card">
                <h2>Busqueda de expedientes</h2>
                <p>Segundo punto de entrada para demostrar como un campo de busqueda puede romper el filtro de consulta.</p>
                <form method="post" id="searchForm">
                    <input type="hidden" name="action" value="search">
                    <div>
                        <label for="term">Folio o nombre</label>
                        <input id="term" type="text" name="term" placeholder="GOB-2026" required>
                    </div>
                    <button type="submit">Buscar</button>
                </form>

                {% if debug_sql %}
                <div class="sql-box">{{ debug_sql }}</div>
                {% endif %}

                {% if results %}
                <div class="results">
                    {% for item in results %}
                    <div class="row">
                        <div>
                            <strong>{{ item[0] }}</strong>
                            <div style="font-size: 0.9rem; color: var(--muted); margin-top: 4px;">{{ item[1] }} | {{ item[2] }} | {{ item[3] }}</div>
                        </div>
                        <div style="color: #a0b0c0; font-size: 0.9rem;">{{ item[4] }}</div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}

                <div style="margin-top: 20px;">
                    <h3 style="color: var(--accent); margin-bottom: 12px;">Ejemplos de inyecciones en búsqueda</h3>
                    <div class="injection-list">
                        {% for example in search_injection_examples %}
                        <div class="injection-item">
                            <div class="injection-header">
                                <strong>{{ example.name }}</strong>
                                <button type="button" class="copy-btn" onclick="fillSearch('{{ example.term|replace("'", "\\'") }}')">Usar</button>
                            </div>
                            <div class="injection-detail">
                                <div><small style="color: var(--muted);">Búsqueda:</small> <code>{{ example.term }}</code></div>
                                <div style="margin-top: 8px; color: #a0b0c0; font-size: 0.9rem;">{{ example.description }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </article>
        </section>

        <p class="footer-note">
            Nota para la presentacion: esta version solo usa datos inventados y funciona en memoria. El proposito es
            enseñar el error de construccion de consultas, no exponer un sistema real.
        </p>
    </main>

    <script>
        function fillLogin(user, pass) {
            document.getElementById('username').value = user;
            document.getElementById('password').value = pass;
            document.getElementById('loginForm').scrollIntoView({ behavior: 'smooth' });
        }

        function fillSearch(term) {
            document.getElementById('term').value = term;
            document.getElementById('searchForm').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    success = None
    info = None
    results = []
    debug_sql = None

    if request.method == "POST":
        action = request.form.get("action", "login")
        cursor = db_conn.cursor()

        try:
            if action == "login":
                username = request.form.get("username", "")
                password = request.form.get("password", "")
                debug_sql = (
                    "SELECT id, username, role, department FROM users WHERE username = '"
                    + username
                    + "' AND password = '"
                    + password
                    + "'"
                )
                cursor.execute(debug_sql)
                user = cursor.fetchone()
                if user:
                    success = f"Acceso concedido para {user['username']} ({user['role']}) - Dept: {user['department']}"
                else:
                    error = "Credenciales invalidas."
                info = "La consulta SQL completa se muestra en pantalla para el ejercicio de clase."
            elif action == "search":
                term = request.form.get("term", "")
                debug_sql = (
                    "SELECT folio, ciudadano, dependencia, estatus, descripcion FROM expedientes WHERE folio LIKE '%"
                    + term
                    + "%' OR ciudadano LIKE '%"
                    + term
                    + "%' OR descripcion LIKE '%"
                    + term
                    + "%'"
                )
                cursor.execute(debug_sql)
                results = cursor.fetchall()
                if results:
                    success = f"Se encontraron {len(results)} expediente(s)."
                else:
                    error = "No se encontraron coincidencias."
                info = "El panel de busqueda replica un segundo punto clasico de inyeccion SQL."
        except Exception as exc:
            error = f"Error en la base de datos: {exc}"

    return render_template_string(
        HTML_TEMPLATE,
        error=error,
        success=success,
        info=info,
        results=results,
        debug_sql=debug_sql,
        injection_examples=INJECTION_EXAMPLES,
        search_injection_examples=SEARCH_INJECTION_EXAMPLES,
        users=[dict(u._mapping) if hasattr(u, '_mapping') else dict(zip(['id', 'username', 'password', 'role', 'department'], u)) for u in db_conn.execute("SELECT * FROM users").fetchall()],
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)