# SSRF Demo

Este proyecto muestra una vulnerabilidad de Server Side Request Forgery (SSRF) usando Flask.

## Características recientes
- Registro mediante DNI (se valida la letra con el algoritmo oficial).
- El registro también solicita nombre completo y permite subir un PDF mayor que 0 bytes.
- Se genera automáticamente un IBAN por usuario y se muestra en la sección `/founds`.
- Para iniciar sesión se utilizan DNI y contraseña.
- Durante la inicialización se crean 250000 usuarios con fondos aleatorios.
- En el dashboard solo se muestran las últimas 300 transferencias para mejorar el rendimiento.
- El dashboard permite realizar transferencias indicando IBAN de destino y monto.
- La interfaz web utiliza TailwindCSS vía CDN con un estilo inspirado en apps fintech modernas.
- La página de inicio presenta publicidad y ventajas si no has iniciado sesión.
- Se añadió una cabecera con degradado y un pie de página con iconos de contacto.
- Las ilustraciones SVG ahora se encuentran incrustadas directamente en las plantillas para mantener el repositorio libre de binarios.
- Los saldos se muestran formateados con miles separados por `.` y decimales con `,`.
- Se incluyó un favicon SVG para identificar la página en el navegador sin archivos binarios.
- El diseño es totalmente responsive y el pie de página queda anclado al final de la pantalla.

## Requisitos
- Python 3
- Dependencias: `pip install -r requirements.txt`

## Uso
1. Ejecuta `python run.py` para iniciar el laboratorio. El script inicializa `bank.db` y lanza dos servidores:
   - **Servidor interno** en `127.0.0.1:5001` (app_internal.py).
   - **Servidor público** en `0.0.0.0:5000` (app_public.py).
   
   También puedes ejecutarlos por separado con `python app_internal.py` y `python app_public.py`.
2. Abre `http://localhost:5000` en tu navegador y registra o inicia sesión con un usuario.
   El formulario de registro solicita DNI (con la letra correcta), nombre completo,
   contraseña y un documento PDF.

## Realizar el ataque SSRF
1. Registra un usuario atacante con un DNI válido, por ejemplo `12345678Z`.
2. Desde el panel, ve a **Verify external URL**.
3. Introduce la URL interna para transferir fondos desde otra cuenta usando los IBAN:
   ```
   http://127.0.0.1:5001/transfer?from=ES1111111111111111111111&to=ES2222222222222222222222&amount=500
   ```
4. El servidor público realizará la petición sin validar la dirección y moverá el dinero indicado a la cuenta del atacante. Vuelve al *dashboard* para comprobarlo.

## Endpoints de la aplicación

- **app_public.py** (puerto 5000)
- `/register`, `/login` y `/dashboard`: registro mediante DNI y documento PDF, inicio de sesión con DNI y contraseña. En el *dashboard* se muestran las transferencias.
  Además cuenta con un formulario para transferir fondos introduciendo un IBAN y un monto.
  Al enviarlo, el servidor hace una petición interna a `http://127.0.0.1:5001/transfer` y muestra
  un mensaje indicando la URL utilizada.
  - `/verify_external`: recibe una URL y la obtiene directamente con `requests.get`. Aquí es donde se aprovecha la SSRF.
- **app_internal.py** (puerto 5001, solo escuchando en `127.0.0.1`)
  - `/users`: lista todos los usuarios registrados con su IBAN.
  - `/founds`: devuelve el balance e IBAN de cada usuario.
  - `/transfer?from=<iban_a>&to=<iban_b>&amount=<n>`: transfiere la cantidad indicada de la cuenta `iban_a` a la `iban_b`.
  - `/transfer_all?to_iban=<iban>`: transfiere todo el dinero de todos los usuarios al `iban` indicado sin autenticación (para fines de laboratorio).

Tras realizar el ataque SSRF, puedes comprobar el nuevo saldo accediendo nuevamente al *dashboard* o consultando directamente el servicio interno en `http://127.0.0.1:5001`.

## Explicación
- El endpoint `/verify_external` en `app_public.py` envía la URL recibida directamente con `requests.get`, permitiendo acceder a servicios internos.
- Una solución sería validar las URLs permitidas o realizar la petición desde el cliente en lugar del servidor.
