# SSRF Demo

Este proyecto muestra una vulnerabilidad de Server Side Request Forgery (SSRF) usando Flask.

## Requisitos
- Python 3
- Dependencias: `pip install -r requirements.txt`

## Uso
1. Ejecuta `python run.py` para iniciar el laboratorio. El script inicializa `bank.db` y lanza dos servidores:
   - **Servidor interno** en `127.0.0.1:5001` (app_internal.py).
   - **Servidor público** en `0.0.0.0:5000` (app_public.py).
   
   También puedes ejecutarlos por separado con `python app_internal.py` y `python app_public.py`.
2. Abre `http://localhost:5000` en tu navegador y registra o inicia sesión con un usuario.

## Realizar el ataque SSRF
1. Registra un usuario atacante, por ejemplo `atacante`.
2. Desde el panel, ve a **Verify external URL**.
3. Introduce la URL interna:
   ```
   http://127.0.0.1:5001/internal/transfer_all?to_user=atacante
   ```
4. El servidor público realizará la petición sin validar la dirección y transferirá el saldo de todos los usuarios al atacante. Vuelve al *dashboard* para comprobarlo.

## Endpoints de la aplicación

- **app_public.py** (puerto 5000)
  - `/register`, `/login` y `/dashboard`: flujo básico de registro e inicio de sesión.
  - `/verify_external`: recibe una URL y la obtiene directamente con `requests.get`. Aquí es donde se aprovecha la SSRF.
- **app_internal.py** (puerto 5001, solo escuchando en `127.0.0.1`)
  - `/internal/transfer_all?to_user=<usuario>`: transfiere todo el dinero de todos los usuarios al indicado en `to_user` sin autenticación.
    Este endpoint se diseñó para estar expuesto únicamente internamente, por lo que el puerto 5001 no debería ser accesible desde Internet.

Tras realizar el ataque SSRF, puedes comprobar el nuevo saldo accediendo nuevamente al *dashboard* o consultando directamente el servicio interno en `http://127.0.0.1:5001`.

## Explicación
- El endpoint `/verify_external` en `app_public.py` envía la URL recibida directamente con `requests.get`, permitiendo acceder a servicios internos.
- Una solución sería validar las URLs permitidas o realizar la petición desde el cliente en lugar del servidor.
