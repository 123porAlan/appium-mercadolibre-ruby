# Challenge: Automatización Móvil de Mercado Libre (Android)

Este repositorio contiene la solución para un reto de automatización móvil, enfocado en probar la funcionalidad de búsqueda y filtrado de la aplicación de Mercado Libre en Android.

**Nota Importante:** Los requisitos originales solicitaban la implementación en Ruby. Esta solución se desarrolló en **Python** con Appium y Pytest.

## Escenario de Prueba

El objetivo del script es automatizar el siguiente flujo de usuario:

1.  Abrir la aplicación de Mercado Libre.
2.  Buscar el término “playstation 5”.
3.  Aplicar el filtro de condición “Nuevos”.
4.  Aplicar el filtro de ubicación “CDMX”.
5.  Ordenar los resultados por “mayor a menor precio”.
6.  Obtener el nombre y el precio de los primeros 5 productos.
7.  Imprimir esta información (nombre y precio) en la consola.

---

## Stack Tecnológico

- **Lenguaje:** Python 3
- **Framework de Pruebas:** Pytest
- **Driver de Automatización:** Appium (con `appium-python-client`)
- **Plataforma:** Android (dispositivo físico)

---

## Cómo Empezar

### Requisitos Previos

1.  Tener Python 3.x instalado.
2.  Tener Appium Server 2.0 instalado (`npm install -g appium`).
3.  Tener el driver UiAutomator2 para Appium (`appium driver install uiautomator2`).
4.  Un dispositivo Android físico con el "Modo Desarrollador" y "Depuración USB" activados.
5.  Tener la aplicación de Mercado Libre instalada en el dispositivo.

### Instalación

1.  Clona este repositorio:

    ```bash
    git clone https://github.com/TU_USUARIO/TU_REPO.git
    cd TU_REPO
    ```

2.  (Recomendado) Crea un entorno virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  Instala las dependencias de Python. (Asegúrate de tener un archivo `requirements.txt` con `pytest`, `appium-python-client` y `selenium`).

    ```bash
    pip install -r requirements.txt
    ```

### Ejecución

1.  Inicia el servidor de Appium en tu terminal:

    ```bash
    appium
    ```

2.  Abre el archivo de prueba (ej. `test_mercadolibre.py`) y **actualiza el `UDID`** en las _capabilities_ para que coincida con el de tu dispositivo:

    ```python
    # ...
    opts.udid = "TU_UDID_AQUI"  # Reemplaza esto
    # ...
    ```

    _Puedes obtener tu UDID con el comando `adb devices`._

3.  Ejecuta la prueba usando Pytest:

    ```bash
    pytest
    ```

La prueba se ejecutará en el dispositivo conectado y verás los resultados impresos en la consola al finalizar.

---

## Proceso de Desarrollo y Desafíos

Quiero ser explícito sobre el proceso, ya que no fue trivial y presentó varios desafíos técnicos.

### Mi Entorno de Trabajo

Es importante mencionar que **no utilicé Android Studio** para este proyecto. Todo el desarrollo y la depuración se realizaron conectando un teléfono Android físico directamente a mi computadora vía USB.

Mi flujo de trabajo principal consistió en tres herramientas:

1.  Mi editor de código (para escribir el script en Python).
2.  La terminal (para correr `adb`, `appium` y `pytest`).
3.  **Appium Inspector**, que fue la herramienta más crítica.

### El Principal Desafío: Localizar Elementos

El reto más grande fue, por mucho, la **localización confiable de elementos** en la app de Mercado Libre.

La aplicación parece estar construida con vistas nativas que no siempre exponen IDs estáticos o _Accessibility IDs_ claros. El primer paso, hacer clic en la barra de búsqueda, fue el más complejo.

- **El Problema:** Un simple `find_element(by=ID, ...).click()` no funcionaba. El elemento parecía recibir el clic pero no abría la pantalla de búsqueda.
- **Mi Proceso de Depuración:** Mi método fue conectar el celular, ejecutar el script y ver cómo fallaba. Inmediatamente después, abría **Appium Inspector** y apuntaba a mi sesión para ver "qué" estaba viendo Appium en ese preciso instante.
- **Descubrimientos:**
  1.  Descubrí que el "botón" de búsqueda inicial no es un `EditText` simple; es un contenedor (`ViewGroup`) con un `TextView` adentro.
  2.  Experimenté con múltiples localizadores (XPath, UiAutomator con `textContains("Buscar en")`, etc.) para encontrar el elemento clicable.
  3.  Incluso después de localizarlo, el `.click()` estándar de Selenium/Appium fallaba. Tuve que probar métodos alternativos (como se ve en el código de diagnóstico) como `click_via_gesture` (coordenadas nativas), `W3C Actions` (simulación de "dedo") e incluso clics por ADB.

Este ciclo de "probar \> fallar \> inspeccionar con Appium Inspector \> refinar locator" se repitió para casi todos los elementos clave, como los botones de filtro ("Nuevos", "CDMX") y las opciones de ordenamiento, que a menudo estaban ocultos o requerían _scrolls_ para ser visibles.
