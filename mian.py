from flask import Flask, render_template_string, request
import sqlite3


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
            role TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE expedientes (
            folio TEXT PRIMARY KEY,
            ciudadano TEXT NOT NULL,
            dependencia TEXT NOT NULL,
            estatus TEXT NOT NULL
        )
        """
    )

    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        [
            (1, "admin", "password123", "Administrador"),
            (2, "auditor", "auditor2026", "Auditor"),
            (3, "invitado", "uabc2026", "Consulta"),
        ],
    )
    cursor.executemany(
        "INSERT INTO expedientes VALUES (?, ?, ?, ?)",
        [
            ("GOB-2026-001", "Mariana Lopez", "Salud", "En revision"),
            ("GOB-2026-002", "Carlos Vega", "Finanzas", "Aprobado"),
            ("GOB-2026-003", "Ana Torres", "Obras Publicas", "Pendiente"),
            ("GOB-2026-004", "Luis Rojas", "Educacion", "Archivado"),
        ],
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
                    demostracion tecnica. En la rama <strong>fixed</strong> la construccion de consultas usa
                    defensas basicas para mostrar la mitigacion de una inyeccion SQL en un entorno controlado.
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
            </aside>
        </section>

        <section class="grid">
            <article class="panel card">
                <h2>Acceso al portal</h2>
                <p>Formulario de autenticacion con consultas parametrizadas y validacion basica de entrada.</p>
                <form method="post">
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
            </article>

            <article class="panel card">
                <h2>Busqueda de expedientes</h2>
                <p>Segundo punto de entrada protegido con consultas parametrizadas y coincidencias seguras.</p>
                <form method="post">
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
                        <strong>{{ item[0] }}</strong>
                        <span>{{ item[1] }} | {{ item[2] }} | {{ item[3] }}</span>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </article>
        </section>

        <p class="footer-note">
            Nota para la presentacion: esta version solo usa datos inventados y funciona en memoria. El proposito es
            enseñar el error de construccion de consultas, no exponer un sistema real.
        </p>
    </main>
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
                username = username.strip()
                password = password.strip()
                if not username or not password:
                    error = "Debes completar usuario y clave."
                else:
                    debug_sql = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
                    cursor.execute(debug_sql, (username, password))
                    user = cursor.fetchone()
                    if user:
                        success = f"Acceso concedido para {user['username']} ({user['role']})."
                    else:
                        error = "Credenciales invalidas."
                    info = "La consulta usa parametros enlazados, no concatenacion de cadenas."
            elif action == "search":
                term = request.form.get("term", "").strip()
                if not term:
                    error = "Ingresa un folio o nombre para buscar."
                else:
                    debug_sql = (
                        "SELECT folio, ciudadano, dependencia, estatus FROM expedientes "
                        "WHERE folio LIKE ? OR ciudadano LIKE ?"
                    )
                    pattern = f"%{term}%"
                    cursor.execute(debug_sql, (pattern, pattern))
                    results = cursor.fetchall()
                    if results:
                        success = f"Se encontraron {len(results)} expediente(s)."
                    else:
                        error = "No se encontraron coincidencias."
                    info = "El filtrado usa marcadores de posicion y no inserta la entrada en el SQL."
        except Exception as exc:
            error = f"Error en la base de datos: {exc}"

    return render_template_string(
        HTML_TEMPLATE,
        error=error,
        success=success,
        info=info,
        results=results,
        debug_sql=debug_sql,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)