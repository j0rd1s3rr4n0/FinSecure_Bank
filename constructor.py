import os
import sqlite3

FOLDER = "finsecure-bank"

# 1. Crear carpeta si no existe
os.makedirs(FOLDER, exist_ok=True)

# 2. Esquema SQL con saldo inicial elevado para Alice
schema_sql = """
CREATE TABLE usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  nombre TEXT NOT NULL,
  saldo REAL DEFAULT 0
);

INSERT INTO usuarios (username, password, nombre, saldo) VALUES
('alice', 'alice123', 'Alice García', 50000000.00),
('bob', 'bob123', 'Bob Sánchez', 850.40),
('eve', 'eve123', 'Eve Hacker', 13.37);
"""

# 3. Guardar schema.sql
with open(os.path.join(FOLDER, "schema.sql"), "w", encoding="utf-8") as f:
    f.write(schema_sql)

# 4. Eliminar la base de datos si ya existe
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
    <title>FinSecure Bank - Acceso Seguro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #0055ff;
            --primary-dark: #003bb3;
            --secondary: #1a1f3d;
            --light-bg: #f7f9ff;
            --card-bg: #ffffff;
            --border: #e1e7ff;
            --success: #00c853;
            --danger: #ed254e;
            --text-light: #6c7493;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        body {
            background: var(--light-bg);
            display: flex;
            min-height: 100vh;
            padding: 20px;
            background-image: linear-gradient(135deg, #f5f7ff 0%, #e6eeff 100%);
        }
        
        .container {
            max-width: 420px;
            margin: auto;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .logo-icon {
            background: var(--primary);
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            box-shadow: 0 6px 15px rgba(0, 85, 255, 0.3);
        }
        
        .logo-text {
            font-size: 28px;
            font-weight: 800;
            color: var(--secondary);
            letter-spacing: -1px;
        }
        
        .logo-subtext {
            color: var(--text-light);
            font-size: 16px;
            max-width: 300px;
            margin: 0 auto;
            line-height: 1.6;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(26, 31, 61, 0.15);
            padding: 40px;
            border: 1px solid var(--border);
        }
        
        .card-title {
            font-size: 24px;
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 30px;
            text-align: center;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-label {
            display: block;
            margin-bottom: 8px;
            color: var(--secondary);
            font-weight: 500;
            font-size: 15px;
        }
        
        .input-field {
            width: 100%;
            padding: 16px 18px;
            border-radius: 14px;
            border: 1px solid var(--border);
            font-size: 16px;
            transition: all 0.2s;
            background: #fafbff;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(0, 85, 255, 0.2);
        }
        
        .btn {
            width: 100%;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 17px;
            padding: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 10px;
            box-shadow: 0 4px 15px rgba(0, 85, 255, 0.3);
        }
        
        .btn:hover {
            background: var(--primary-dark);
            box-shadow: 0 6px 20px rgba(0, 85, 255, 0.4);
            transform: translateY(-2px);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .error-message {
            background: rgba(237, 37, 78, 0.1);
            color: var(--danger);
            padding: 14px;
            border-radius: 12px;
            margin-bottom: 25px;
            text-align: center;
            font-size: 15px;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: var(--text-light);
            font-size: 14px;
        }
        
        .footer a {
            color: var(--primary);
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <div class="logo-text">FinSecure</div>
            </div>
            <p class="logo-subtext">Banca digital segura con protección avanzada de fondos</p>
        </div>
        
        <div class="card">
            <h2 class="card-title">Acceso a tu cuenta</h2>
            
            <?php if(isset($err)): ?>
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i> <?=htmlspecialchars($err)?>
                </div>
            <?php endif; ?>
            
            <form method="POST">
                <div class="input-group">
                    <label class="input-label">Usuario</label>
                    <input class="input-field" name="username" placeholder="Introduce tu usuario" required autofocus>
                </div>
                
                <div class="input-group">
                    <label class="input-label">Contraseña</label>
                    <input class="input-field" type="password" name="password" placeholder="••••••••" required>
                </div>
                
                <button class="btn" type="submit">
                    <i class="fas fa-lock-open"></i> Acceder a mi cuenta
                </button>
            </form>
        </div>
        
        <div class="footer">
            <p>¿Problemas para acceder? <a href="#">Contactar con soporte</a></p>
            <p style="margin-top: 8px;">FinSecure Bank © 2023 - Todos los derechos reservados</p>
        </div>
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
    <title>Panel | FinSecure Bank</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #0055ff;
            --primary-dark: #003bb3;
            --secondary: #1a1f3d;
            --light-bg: #f7f9ff;
            --card-bg: #ffffff;
            --border: #e1e7ff;
            --success: #00c853;
            --danger: #ed254e;
            --text-light: #6c7493;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        body {
            background: var(--light-bg);
            min-height: 100vh;
        }
        
        .navbar {
            background: var(--card-bg);
            padding: 20px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 15px rgba(26, 31, 61, 0.1);
            border-bottom: 1px solid var(--border);
        }
        
        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .brand-icon {
            background: var(--primary);
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
        }
        
        .brand-text {
            font-size: 22px;
            font-weight: 800;
            color: var(--secondary);
            letter-spacing: -0.5px;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .user-info {
            text-align: right;
        }
        
        .user-name {
            font-weight: 600;
            color: var(--secondary);
            font-size: 16px;
        }
        
        .user-account {
            color: var(--text-light);
            font-size: 14px;
        }
        
        .logout-btn {
            background: rgba(237, 37, 78, 0.1);
            color: var(--danger);
            border: none;
            border-radius: 10px;
            padding: 8px 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .logout-btn:hover {
            background: rgba(237, 37, 78, 0.2);
        }
        
        .main {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 40px;
        }
        
        .welcome {
            margin-bottom: 40px;
        }
        
        .welcome-title {
            font-size: 32px;
            font-weight: 800;
            color: var(--secondary);
            margin-bottom: 10px;
            letter-spacing: -1px;
        }
        
        .welcome-subtitle {
            color: var(--text-light);
            font-size: 18px;
            max-width: 600px;
            line-height: 1.6;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(26, 31, 61, 0.1);
            padding: 35px;
            border: 1px solid var(--border);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        
        .card-title {
            font-size: 22px;
            font-weight: 700;
            color: var(--secondary);
        }
        
        .card-icon {
            width: 50px;
            height: 50px;
            background: rgba(0, 85, 255, 0.1);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-size: 22px;
        }
        
        .balance-amount {
            color: var(--primary);
            font-size: 48px;
            font-weight: 800;
            margin: 20px 0;
            letter-spacing: -1.5px;
        }
        
        .balance-label {
            color: var(--text-light);
            font-size: 16px;
        }
        
        .actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 30px;
        }
        
        .action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--light-bg);
            border-radius: 16px;
            padding: 25px 15px;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s;
            border: 1px solid var(--border);
        }
        
        .action-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 15px rgba(0, 85, 255, 0.15);
            border-color: var(--primary);
        }
        
        .action-icon {
            width: 50px;
            height: 50px;
            background: var(--primary);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 22px;
            margin-bottom: 15px;
        }
        
        .action-text {
            font-weight: 600;
            color: var(--secondary);
            font-size: 16px;
        }
        
        .recent-activity {
            list-style: none;
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            padding: 20px 0;
            border-bottom: 1px solid var(--border);
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 18px;
        }
        
        .income .activity-icon {
            background: rgba(0, 200, 83, 0.1);
            color: var(--success);
        }
        
        .expense .activity-icon {
            background: rgba(237, 37, 78, 0.1);
            color: var(--danger);
        }
        
        .activity-details {
            flex: 1;
        }
        
        .activity-title {
            font-weight: 600;
            color: var(--secondary);
            margin-bottom: 5px;
        }
        
        .activity-description {
            color: var(--text-light);
            font-size: 14px;
        }
        
        .activity-amount {
            font-weight: 700;
            font-size: 18px;
        }
        
        .income .activity-amount {
            color: var(--success);
        }
        
        .expense .activity-amount {
            color: var(--danger);
        }
        
        .security-note {
            background: rgba(255, 193, 7, 0.1);
            border-radius: 16px;
            padding: 20px;
            margin-top: 30px;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }
        
        .security-title {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #ff9800;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .security-text {
            color: #ff9800;
            font-size: 14px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="brand">
            <div class="brand-icon">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div class="brand-text">FinSecure</div>
        </div>
        
        <div class="user-menu">
            <div class="user-info">
                <div class="user-name"><?=htmlspecialchars($user['nombre'])?></div>
                <div class="user-account">Cuenta: <?=htmlspecialchars($user['username'])?></div>
            </div>
            <a href="logout.php"><button class="logout-btn">Salir</button></a>
        </div>
    </nav>
    
    <div class="main">
        <div class="welcome">
            <h1 class="welcome-title">Panel de control</h1>
            <p class="welcome-subtitle">Bienvenido a tu banca online segura. Gestiona tus finanzas con total confianza.</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Resumen de cuenta</h2>
                    <div class="card-icon">
                        <i class="fas fa-wallet"></i>
                    </div>
                </div>
                
                <div class="balance-amount">€ <?=number_format($user['saldo'], 2, ',', '.')?></div>
                <div class="balance-label">Saldo disponible</div>
                
                <div class="actions">
                    <a href="fetch-info.php" class="action-btn">
                        <div class="action-icon">
                            <i class="fas fa-globe"></i>
                        </div>
                        <div class="action-text">Consultas externas</div>
                    </a>
                    
                    <a href="retirar.php" class="action-btn">
                        <div class="action-icon">
                            <i class="fas fa-money-bill-wave"></i>
                        </div>
                        <div class="action-text">Retirar fondos</div>
                    </a>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Actividad reciente</h2>
                    <div class="card-icon">
                        <i class="fas fa-history"></i>
                    </div>
                </div>
                
                <ul class="recent-activity">
                    <li class="activity-item income">
                        <div class="activity-icon">
                            <i class="fas fa-arrow-down"></i>
                        </div>
                        <div class="activity-details">
                            <div class="activity-title">Depósito de nómina</div>
                            <div class="activity-description">Empleador: TechCorp SL</div>
                        </div>
                        <div class="activity-amount">+€1,850.75</div>
                    </li>
                    
                    <li class="activity-item expense">
                        <div class="activity-icon">
                            <i class="fas fa-arrow-up"></i>
                        </div>
                        <div class="activity-details">
                            <div class="activity-title">Transferencia a Bob Sánchez</div>
                            <div class="activity-description">Concepto: Préstamo</div>
                        </div>
                        <div class="activity-amount">-€250.00</div>
                    </li>
                    
                    <li class="activity-item expense">
                        <div class="activity-icon">
                            <i class="fas fa-shopping-cart"></i>
                        </div>
                        <div class="activity-details">
                            <div class="activity-title">Compra online</div>
                            <div class="activity-description">Amazon Marketplace</div>
                        </div>
                        <div class="activity-amount">-€89.99</div>
                    </li>
                </ul>
                
                <div class="security-note">
                    <div class="security-title">
                        <i class="fas fa-shield-alt"></i> Protección FinSecure
                    </div>
                    <p class="security-text">Tus fondos están protegidos por nuestro sistema de seguridad avanzado. Detectamos y bloqueamos actividades sospechosas automáticamente.</p>
                </div>
            </div>
        </div>
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
    <title>Consulta Externa | FinSecure Bank</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #0055ff;
            --primary-dark: #003bb3;
            --secondary: #1a1f3d;
            --light-bg: #f7f9ff;
            --card-bg: #ffffff;
            --border: #e1e7ff;
            --success: #00c853;
            --danger: #ed254e;
            --text-light: #6c7493;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        body {
            background: var(--light-bg);
            min-height: 100vh;
        }
        
        .navbar {
            background: var(--card-bg);
            padding: 20px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 15px rgba(26, 31, 61, 0.1);
            border-bottom: 1px solid var(--border);
        }
        
        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .brand-icon {
            background: var(--primary);
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
        }
        
        .brand-text {
            font-size: 22px;
            font-weight: 800;
            color: var(--secondary);
            letter-spacing: -0.5px;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 25px;
        }
        
        .back-btn:hover {
            text-decoration: underline;
        }
        
        .main {
            max-width: 800px;
            margin: 40px auto;
            padding: 0 40px;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(26, 31, 61, 0.1);
            padding: 35px;
            border: 1px solid var(--border);
        }
        
        .card-header {
            margin-bottom: 30px;
        }
        
        .card-title {
            font-size: 28px;
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 10px;
        }
        
        .card-subtitle {
            color: var(--text-light);
            font-size: 17px;
            line-height: 1.6;
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        .input-label {
            display: block;
            margin-bottom: 12px;
            color: var(--secondary);
            font-weight: 600;
            font-size: 16px;
        }
        
        .input-field {
            width: 100%;
            padding: 18px 20px;
            border-radius: 16px;
            border: 1px solid var(--border);
            font-size: 16px;
            transition: all 0.2s;
            background: #fafbff;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(0, 85, 255, 0.2);
        }
        
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 17px;
            padding: 18px 35px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        
        .btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 85, 255, 0.3);
        }
        
        .result-container {
            margin-top: 40px;
            background: #f8faff;
            border-radius: 16px;
            border: 1px solid var(--border);
            padding: 25px;
            display: none;
        }
        
        .result-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        pre {
            background: #1a1f3d;
            color: #f1f5ff;
            border-radius: 12px;
            padding: 25px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 15px;
            line-height: 1.5;
        }
        
        .security-warning {
            background: rgba(237, 37, 78, 0.08);
            border-radius: 16px;
            padding: 20px;
            margin-top: 30px;
            border: 1px solid rgba(237, 37, 78, 0.2);
        }
        
        .warning-title {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--danger);
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .warning-text {
            color: var(--danger);
            font-size: 14px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="brand">
            <div class="brand-icon">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div class="brand-text">FinSecure</div>
        </div>
    </nav>
    
    <div class="main">
        <a href="panel.php" class="back-btn">
            <i class="fas fa-arrow-left"></i> Volver al panel
        </a>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Consulta de información externa</h2>
                <p class="card-subtitle">Obtén datos de servicios externos utilizando nuestra conexión segura. Introduce una URL válida para recuperar información.</p>
            </div>
            
            <form method="GET">
                <div class="input-group">
                    <label class="input-label">URL del recurso externo</label>
                    <input class="input-field" type="url" name="url" placeholder="https://ejemplo.com/api/datos" required value="<?=isset($_GET['url']) ? htmlspecialchars($_GET['url']) : ''?>">
                </div>
                
                <button class="btn" type="submit">
                    <i class="fas fa-search"></i> Consultar información
                </button>
            </form>
            
            <?php
            if (isset($_GET['url'])) {
                $url = $_GET['url'];
                echo "<div class='result-container' style='display:block;'>";
                echo "<div class='result-title'><i class='fas fa-file-alt'></i> Resultado de <code>".htmlspecialchars($url)."</code></div>";
                // ----------- VULNERABILIDAD SSRF AQUÍ -----------
                $data = @file_get_contents($url);
                echo "<pre>".htmlspecialchars($data)."</pre>";
                echo "</div>";
            }
            ?>
            
            <div class="security-warning">
                <div class="warning-title">
                    <i class="fas fa-exclamation-triangle"></i> Advertencia de seguridad
                </div>
                <p class="warning-text">Por tu seguridad, solo consulta servicios confiables. FinSecure no se responsabiliza por el contenido obtenido de fuentes externas.</p>
            </div>
        </div>
    </div>
    
    <script>
        // Mostrar contenedor de resultados si hay una consulta
        <?php if(isset($_GET['url'])): ?>
            document.querySelector('.result-container').style.display = 'block';
        <?php endif; ?>
    </script>
</body>
</html>
"""
with open(os.path.join(FOLDER, "fetch-info.php"), "w", encoding="utf-8") as f:
    f.write(fetch_info_php)

# 10. transferir.php (solo para localhost)
transferir_php = """<?php
// Solo accesible desde localhost
$allowed_ips = ['127.0.0.1', '::1'];
if (!in_array($_SERVER['REMOTE_ADDR'], $allowed_ips)) {
    header("HTTP/1.0 403 Forbidden");
    die("Acceso restringido. Solo disponible para el sistema interno.");
}

require_once 'db.php';

// Obtener parámetros
$origen = $_GET['origen'] ?? '';
$destino = $_GET['destino'] ?? '';
$monto = floatval($_GET['monto'] ?? 0);

// Validar parámetros
if (empty($origen) || empty($destino) || $monto <= 0) {
    die("Parámetros inválidos. Se requieren origen, destino y monto.");
}

// Verificar saldo del origen
$stmt = $db->prepare("SELECT saldo FROM usuarios WHERE username = :u");
$stmt->bindValue(':u', $origen, SQLITE3_TEXT);
$result = $stmt->execute();
$row = $result->fetchArray(SQLITE3_ASSOC);

if (!$row) {
    die("Usuario origen no encontrado");
}

if ($row['saldo'] < $monto) {
    die("Saldo insuficiente");
}

// Verificar existencia del destino
$stmt = $db->prepare("SELECT 1 FROM usuarios WHERE username = :u");
$stmt->bindValue(':u', $destino, SQLITE3_TEXT);
$result = $stmt->execute();
$destino_existe = $result->fetchArray();

if (!$destino_existe) {
    die("Usuario destino no encontrado");
}

// Realizar transferencia
$db->exec('BEGIN');
try {
    // Restar del origen
    $update_origen = $db->prepare("UPDATE usuarios SET saldo = saldo - :m WHERE username = :u");
    $update_origen->bindValue(':m', $monto, SQLITE3_FLOAT);
    $update_origen->bindValue(':u', $origen, SQLITE3_TEXT);
    $update_origen->execute();

    // Sumar al destino
    $update_destino = $db->prepare("UPDATE usuarios SET saldo = saldo + :m WHERE username = :u");
    $update_destino->bindValue(':m', $monto, SQLITE3_FLOAT);
    $update_destino->bindValue(':u', $destino, SQLITE3_TEXT);
    $update_destino->execute();

    $db->exec('COMMIT');
    echo "Transferencia exitosa: €" . number_format($monto, 2) . " transferidos de $origen a $destino";
} catch (Exception $e) {
    $db->exec('ROLLBACK');
    die("Error en la transferencia: " . $e->getMessage());
}
?>
"""
with open(os.path.join(FOLDER, "transferir.php"), "w", encoding="utf-8") as f:
    f.write(transferir_php)

# 11. listar-usuarios.php (solo para localhost)
listar_usuarios_php = """<?php
// Solo accesible desde localhost
$allowed_ips = ['127.0.0.1', '::1'];
if (!in_array($_SERVER['REMOTE_ADDR'], $allowed_ips)) {
    header("HTTP/1.0 403 Forbidden");
    die("Acceso restringido. Solo disponible para administradores locales.");
}

require_once 'db.php';
$res = $db->query("SELECT username, nombre, saldo FROM usuarios");
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Usuarios del banco | FinSecure</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #0055ff;
            --secondary: #1a1f3d;
            --light-bg: #f7f9ff;
            --card-bg: #ffffff;
            --border: #e1e7ff;
            --text-light: #6c7493;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        body {
            background: var(--light-bg);
            min-height: 100vh;
            padding: 40px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .logo-icon {
            background: var(--primary);
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
        }
        
        .logo-text {
            font-size: 28px;
            font-weight: 800;
            color: var(--secondary);
            letter-spacing: -1px;
        }
        
        .admin-title {
            font-size: 24px;
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 30px;
            text-align: center;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(26, 31, 61, 0.15);
            padding: 40px;
            border: 1px solid var(--border);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: #f8faff;
            border-radius: 16px;
            overflow: hidden;
        }
        
        th, td {
            padding: 16px 20px;
            text-align: left;
        }
        
        th {
            background: #eef2ff;
            color: var(--secondary);
            font-weight: 700;
            border-bottom: 2px solid var(--border);
        }
        
        tr:nth-child(even) {
            background: #f5f7ff;
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: var(--text-light);
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <div class="logo-text">FinSecure</div>
            </div>
            <h1 class="admin-title">Usuarios y Saldos</h1>
        </div>
        
        <div class="card">
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
        
        <div class="footer">
            <p>Acceso restringido a administradores | FinSecure Bank © 2023</p>
        </div>
    </div>
</body>
</html>
"""
with open(os.path.join(FOLDER, "listar-usuarios.php"), "w", encoding="utf-8") as f:
    f.write(listar_usuarios_php)

# 12. retirar.php (funcionalidad de retiro con flag)
retirar_php = """<?php
session_start();
require_once 'db.php';
if (!isset($_SESSION['user'])) header("Location: index.php");

$username = $_SESSION['user'];
$flag = "flag{EnoraBuenaHasVulneradoElBanco}";

// Obtener saldo actual
$stmt = $db->prepare("SELECT saldo, nombre FROM usuarios WHERE username = :u");
$stmt->bindValue(':u', $username, SQLITE3_TEXT);
$user = $stmt->execute()->fetchArray(SQLITE3_ASSOC);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $monto = floatval($_POST['monto'] ?? 0);
    
    if ($monto <= 0) {
        $error = "Monto inválido. Introduce un valor positivo.";
    } elseif ($monto > $user['saldo']) {
        $error = "Saldo insuficiente para realizar esta operación.";
    } else {
        // Verificar si tiene 30 millones para mostrar la flag
        $mostrar_flag = ($user['saldo'] >= 30000000);
        
        // Actualizar saldo
        $update = $db->prepare("UPDATE usuarios SET saldo = saldo - :m WHERE username = :u");
        $update->bindValue(':m', $monto, SQLITE3_FLOAT);
        $update->bindValue(':u', $username, SQLITE3_TEXT);
        $update->execute();
        
        // Actualizar datos de usuario
        $stmt->bindValue(':u', $username, SQLITE3_TEXT);
        $user = $stmt->execute()->fetchArray(SQLITE3_ASSOC);
        
        if ($mostrar_flag) {
            $success = "¡Felicidades! " . $flag;
        } else {
            $success = "Retiro exitoso de €" . number_format($monto, 2, ',', '.');
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Retirar Fondos | FinSecure Bank</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #0055ff;
            --primary-dark: #003bb3;
            --secondary: #1a1f3d;
            --light-bg: #f7f9ff;
            --card-bg: #ffffff;
            --border: #e1e7ff;
            --success: #00c853;
            --danger: #ed254e;
            --text-light: #6c7493;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        body {
            background: var(--light-bg);
            min-height: 100vh;
        }
        
        .navbar {
            background: var(--card-bg);
            padding: 20px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 15px rgba(26, 31, 61, 0.1);
            border-bottom: 1px solid var(--border);
        }
        
        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .brand-icon {
            background: var(--primary);
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
        }
        
        .brand-text {
            font-size: 22px;
            font-weight: 800;
            color: var(--secondary);
            letter-spacing: -0.5px;
        }
        
        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 25px;
        }
        
        .back-btn:hover {
            text-decoration: underline;
        }
        
        .main {
            max-width: 500px;
            margin: 40px auto;
            padding: 0 40px;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(26, 31, 61, 0.1);
            padding: 35px;
            border: 1px solid var(--border);
        }
        
        .card-header {
            margin-bottom: 30px;
        }
        
        .card-title {
            font-size: 28px;
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 10px;
        }
        
        .card-subtitle {
            color: var(--text-light);
            font-size: 17px;
            line-height: 1.6;
        }
        
        .balance-info {
            background: #f8faff;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .balance-label {
            color: var(--text-light);
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .balance-amount {
            color: var(--primary);
            font-size: 40px;
            font-weight: 800;
            letter-spacing: -1.5px;
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        .input-label {
            display: block;
            margin-bottom: 12px;
            color: var(--secondary);
            font-weight: 600;
            font-size: 16px;
        }
        
        .input-field {
            width: 100%;
            padding: 18px 20px;
            border-radius: 16px;
            border: 1px solid var(--border);
            font-size: 16px;
            transition: all 0.2s;
            background: #fafbff;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(0, 85, 255, 0.2);
        }
        
        .btn {
            width: 100%;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 17px;
            padding: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 85, 255, 0.3);
        }
        
        .error-message {
            background: rgba(237, 37, 78, 0.1);
            color: var(--danger);
            padding: 16px;
            border-radius: 14px;
            margin-bottom: 25px;
            text-align: center;
            font-size: 15px;
        }
        
        .success-message {
            background: rgba(0, 200, 83, 0.1);
            color: var(--success);
            padding: 16px;
            border-radius: 14px;
            margin-bottom: 25px;
            text-align: center;
            font-size: 15px;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="brand">
            <div class="brand-icon">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div class="brand-text">FinSecure</div>
        </div>
    </nav>
    
    <div class="main">
        <a href="panel.php" class="back-btn">
            <i class="fas fa-arrow-left"></i> Volver al panel
        </a>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Retirar fondos</h2>
                <p class="card-subtitle">Transfiere dinero a tu cuenta externa o solicita un retiro en efectivo.</p>
            </div>
            
            <div class="balance-info">
                <div class="balance-label">Saldo disponible</div>
                <div class="balance-amount">€ <?=number_format($user['saldo'], 2, ',', '.')?></div>
            </div>
            
            <form method="POST">
                <div class="input-group">
                    <label class="input-label">Monto a retirar (€)</label>
                    <input class="input-field" type="number" step="0.01" min="0.01" name="monto" placeholder="Ej: 500.00" required>
                </div>
                
                <?php if(isset($error)): ?>
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i> <?=htmlspecialchars($error)?>
                    </div>
                <?php endif; ?>
                
                <?php if(isset($success)): ?>
                    <div class="success-message">
                        <i class="fas fa-check-circle"></i> <?=htmlspecialchars($success)?>
                    </div>
                <?php endif; ?>
                
                <button class="btn" type="submit">
                    <i class="fas fa-money-bill-wave"></i> Confirmar retiro
                </button>
            </form>
        </div>
    </div>
</body>
</html>
"""
with open(os.path.join(FOLDER, "retirar.php"), "w", encoding="utf-8") as f:
    f.write(retirar_php)

# 13. logout.php
logout_php = """<?php
session_start();
session_destroy();
header("Location: index.php");
exit;
?>
"""
with open(os.path.join(FOLDER, "logout.php"), "w", encoding="utf-8") as f:
    f.write(logout_php)

# Mensaje final
print("\n¡Servidor bancario FinSecure creado con éxito!")
print("=============================================")
print("Todos los archivos se han generado en la carpeta 'finsecure-bank'")
print("\nPara iniciar el servidor:")
print("    cd finsecure-bank && php -S 0.0.0.0:443")
print("\nAccede en tu navegador: http://localhost:443")
print("\nCredenciales de acceso:")
print("    alice / alice123  (50 millones €)")
print("    bob   / bob123")
print("    eve   / eve123")
print("\nPara explotar la vulnerabilidad SSRF:")
print("1. Inicia sesión como eve (eve/eve123)")
print("2. En el panel, ve a 'Consultas externas'")
print("3. Usa esta URL para transferir fondos:")
print("   http://localhost:443/transferir.php?origen=alice&destino=eve&monto=30000000")
print("4. Regresa al panel y haz clic en 'Retirar fondos'")
print("5. Realiza cualquier retiro para obtener la flag\n")