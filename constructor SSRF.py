import os
import sqlite3

FOLDER = "banco-ssrf"

# 1. Crear carpeta si no existe
os.makedirs(FOLDER, exist_ok=True)

# 2. Esquema SQL
schema_sql = """
CREATE TABLE usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  nombre TEXT NOT NULL,
  saldo REAL DEFAULT 0
);

INSERT INTO usuarios (username, password, nombre, saldo) VALUES
('alice', 'alice123', 'Alice García', 1000.25),
('bob', 'bob123', 'Bob Sánchez', 850.40),
('eve', 'eve123', 'Eve Hacker', 13.37);
"""

# 3. Guardar schema.sql
with open(os.path.join(FOLDER, "schema.sql"), "w", encoding="utf-8") as f:
    f.write(schema_sql)

# 4. Eliminar la base de datos si ya existe (evitar errores)
db_path = os.path.join(FOLDER, "banco.db")
if os.path.exists(db_path):
    os.remove(db_path)

# 5. Crear base de datos usando sqlite3
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.executescript(schema_sql)
conn.commit()
conn.close()

# 6. db.php
db_php = """<?php
$db = new SQLite3('banco.db');
?>
"""
with open(os.path.join(FOLDER, "db.php"), "w", encoding="utf-8") as f:
    f.write(db_php)

# 7. index.php (login)
index_php = """<?php
session_start();
require_once 'db.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    $stmt = $db->prepare("SELECT * FROM usuarios WHERE username = :u AND password = :p");
    $stmt->bindValue(':u', $username, SQLITE3_TEXT);
    $stmt->bindValue(':p', $password, SQLITE3_TEXT);
    $row = $stmt->execute()->fetchArray(SQLITE3_ASSOC);
    if ($row) {
        $_SESSION['user'] = $row['username'];
        header("Location: panel.php");
        exit;
    } else {
        $err = "Usuario o contraseña incorrectos";
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso Banco Online</title>
    <style>
        body { background: #f7f9fa; font-family: 'Inter', Arial, sans-serif; margin: 0; }
        .centered { max-width: 350px; margin: 80px auto; background: #fff; border-radius: 18px; box-shadow: 0 8px 24px #123fa333; padding: 40px 32px 32px; }
        .title { font-size: 2rem; font-weight: 700; color: #212c4f; margin-bottom: 24px; letter-spacing: -1px; }
        .input { width: 100%; padding: 14px 10px; border-radius: 12px; border: 1px solid #dae3ed; margin-bottom: 16px; font-size: 1rem; }
        .btn { width: 100%; background: #235aff; color: #fff; border: none; border-radius: 12px; font-size: 1rem; padding: 14px 0; font-weight: 600; cursor: pointer; transition: background .2s;}
        .btn:hover { background: #183bb6; }
        .error { color: #ed254e; margin-bottom: 12px; text-align: center; }
        .logo { background: #235aff; border-radius: 50%; width: 46px; height: 46px; margin: 0 auto 14px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; font-size: 1.4rem; letter-spacing: -.5px; }
    </style>
</head>
<body>
    <div class="centered">
        <div class="logo">BK</div>
        <div class="title">Banco Online</div>
        <?php if(isset($err)): ?>
            <div class="error"><?=htmlspecialchars($err)?></div>
        <?php endif; ?>
        <form method="POST">
            <input class="input" name="username" placeholder="Usuario" required>
            <input class="input" type="password" name="password" placeholder="Contraseña" required>
            <button class="btn" type="submit">Entrar</button>
        </form>
    </div>
</body>
</html>
"""
with open(os.path.join(FOLDER, "index.php"), "w", encoding="utf-8") as f:
    f.write(index_php)

# 8. panel.php (panel de usuario)
panel_php = """<?php
session_start();
require_once 'db.php';
if (!isset($_SESSION['user'])) header("Location: index.php");

$username = $_SESSION['user'];
$stmt = $db->prepare("SELECT * FROM usuarios WHERE username = :u");
$stmt->bindValue(':u', $username, SQLITE3_TEXT);
$user = $stmt->execute()->fetchArray(SQLITE3_ASSOC);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel | Banco Online</title>
    <style>
        body { background: #f7f9fa; font-family: 'Inter', Arial, sans-serif; margin: 0; }
        .header { background: #fff; padding: 28px 0 8px 0; text-align: center; border-bottom: 1.5px solid #e4eaf2; }
        .logo { background: #235aff; border-radius: 50%; width: 38px; height: 38px; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; font-size: 1.1rem; }
        .main { max-width: 390px; margin: 36px auto 0; }
        .card { background: #f4f6fd; border-radius: 22px; padding: 28px 30px 18px; box-shadow: 0 4px 24px #23308a11; }
        .name { font-size: 1.2rem; font-weight: 600; color: #212c4f; margin-bottom: 3px; }
        .balance { color: #235aff; font-size: 2.3rem; font-weight: 700; margin: 13px 0 16px; letter-spacing: -1px; }
        .actions { margin-top: 30px; }
        .btn { background: #235aff; color: #fff; border: none; border-radius: 14px; font-size: 1rem; padding: 14px 0; width: 100%; font-weight: 600; cursor: pointer; transition: background .2s;}
        .btn:hover { background: #183bb6; }
        .logout { display: block; text-align: center; color: #8992b3; margin: 40px 0 0; font-size: .97rem; text-decoration: none; }
        .logout:hover { color: #212c4f; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">BK</div>
    </div>
    <div class="main">
        <div class="card">
            <div class="name"><?=htmlspecialchars($user['nombre'])?></div>
            <div style="color: #b2b6ca; font-size: .98rem; margin-bottom: 7px;">Cuenta personal</div>
            <div class="balance">€ <?=number_format($user['saldo'], 2, ',', '.')?></div>
            <div class="actions">
                <a href="fetch-info.php"><button class="btn">Consultar información externa</button></a>
            </div>
        </div>
        <a class="logout" href="logout.php">Cerrar sesión</a>
    </div>
</body>
</html>
"""
with open(os.path.join(FOLDER, "panel.php"), "w", encoding="utf-8") as f:
    f.write(panel_php)

# 9. fetch-info.php (SSRF vulnerable)
fetch_info_php = """<?php
session_start();
if (!isset($_SESSION['user'])) header("Location: index.php");
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Consulta Externa | Banco Online</title>
    <style>
        body { background: #f7f9fa; font-family: 'Inter', Arial, sans-serif; margin: 0;}
        .header { background: #fff; padding: 20px 0 10px 0; text-align: center; border-bottom: 1.5px solid #e4eaf2; }
        .logo { background: #235aff; border-radius: 50%; width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; font-size: 1rem; }
        .container { max-width: 390px; margin: 40px auto 0; background: #fff; border-radius: 18px; box-shadow: 0 8px 24px #123fa333; padding: 36px 28px 22px; }
        .title { font-size: 1.15rem; color: #235aff; font-weight: 600; margin-bottom: 25px; }
        .input { width: 100%; padding: 12px 8px; border-radius: 10px; border: 1px solid #dae3ed; font-size: 1rem; margin-bottom: 14px; }
        .btn { width: 100%; background: #235aff; color: #fff; border: none; border-radius: 10px; font-size: 1rem; padding: 12px 0; font-weight: 600; cursor: pointer; transition: background .2s;}
        .btn:hover { background: #183bb6; }
        pre { background: #f4f6fd; border-radius: 10px; padding: 15px; margin-top: 18px; font-size: 0.95rem; color: #232849; overflow-x: auto;}
        a { color: #235aff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">BK</div>
    </div>
    <div class="container">
        <div class="title">Consultar información externa</div>
        <form method="GET">
            <input class="input" type="url" name="url" placeholder="Introduce una URL (http://...)" required value="<?=isset($_GET['url']) ? htmlspecialchars($_GET['url']) : ''?>">
            <button class="btn" type="submit">Consultar</button>
        </form>
        <?php
        if (isset($_GET['url'])) {
            $url = $_GET['url'];
            echo "<div style='margin-top:20px;'><b>Resultado de <code>".htmlspecialchars($url)."</code>:</b></div>";
            // ----------- VULNERABILIDAD SSRF AQUÍ -----------
            $data = @file_get_contents($url);
            echo "<pre>".htmlspecialchars($data)."</pre>";
        }
        ?>
        <a href="panel.php">&larr; Volver al panel</a>
    </div>
</body>
</html>
"""
with open(os.path.join(FOLDER, "fetch-info.php"), "w", encoding="utf-8") as f:
    f.write(fetch_info_php)

# 10. listar-usuarios.php (solo para localhost)
listar_usuarios_php = """<?php
if ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1' && $_SERVER['REMOTE_ADDR'] !== '::1') {
    header("HTTP/1.0 403 Forbidden");
    die("Solo accesible desde localhost");
}
require_once 'db.php';
$res = $db->query("SELECT username, nombre, saldo FROM usuarios");
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Usuarios del banco</title>
    <style>
        body { background: #f7f9fa; font-family: 'Inter', Arial, sans-serif; margin: 0; }
        .main { max-width: 380px; margin: 38px auto; background: #fff; border-radius: 18px; box-shadow: 0 8px 24px #123fa333; padding: 32px 30px 16px; }
        .title { font-size: 1.2rem; color: #235aff; font-weight: 700; margin-bottom: 24px;}
        table { width: 100%; border-collapse: collapse; background: #f4f6fd; border-radius: 12px; overflow: hidden;}
        th, td { padding: 10px 7px; text-align: left; font-size: .99rem;}
        th { color: #26376b; font-weight: 600; border-bottom: 2px solid #e4eaf2;}
        tr:not(:last-child) td { border-bottom: 1px solid #e4eaf2;}
    </style>
</head>
<body>
    <div class="main">
        <div class="title">Usuarios y saldos</div>
        <table>
            <tr>
                <th>Usuario</th>
                <th>Nombre</th>
                <th>Saldo (€)</th>
            </tr>
            <?php while($row = $res->fetchArray(SQLITE3_ASSOC)): ?>
            <tr>
                <td><?=htmlspecialchars($row['username'])?></td>
                <td><?=htmlspecialchars($row['nombre'])?></td>
                <td><?=number_format($row['saldo'],2,',','.')?></td>
            </tr>
            <?php endwhile; ?>
        </table>
    </div>
</body>
</html>
"""
with open(os.path.join(FOLDER, "listar-usuarios.php"), "w", encoding="utf-8") as f:
    f.write(listar_usuarios_php)

# 11. logout.php
logout_php = """<?php
session_start();
session_destroy();
header("Location: index.php");
exit;
?>
"""
with open(os.path.join(FOLDER, "logout.php"), "w", encoding="utf-8") as f:
    f.write(logout_php)

print("¡Listo! Todos los archivos han sido creados en la carpeta 'banco-ssrf'.")
print("Puedes copiar la carpeta a tu servidor PHP o ejecutar:")
print("    cd banco-ssrf && php -S 0.0.0.0:8080")
print("Acceso: alice/alice123 | bob/bob123 | eve/eve123")
