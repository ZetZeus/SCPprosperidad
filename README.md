
# Sistema control de producción

El siguiente sistema tiene como función principal registrar la información de diversos centros de trabajos presentes en planta a través del uso de una Web App realizada en Django utilizando formularios y registrandolos en una base de datos para una posterior visualización BI a elección.



## Tecnologías utilizadas

- Django 4.2.1
- Python 3.9
- PostgreSQL 14
## Instalación

Para un correcto uso del sistema sigue los siguientes pasos:

- Asegurate de tener instalado PostgreSQL 14 y Python 3.9 en tu sistema operativo
- Crear la base de datos en PostgreSQL a través de pgAdmin u otro administrador de BD (no es necesaria la creación de tablas, ya que con *migrate* en Django las crea además de generar tablas propias de este framework)
- Crear entorno virtual para la instalación y ejecución del programa
- Clonar el repositorio desde la parte superior de la página
- Instalar dependencias (install_requirements.bat)
- Revisar si archivos relacionados a PostgreSQL se encuentran correctamente instalados, tales como psycopg psycopg2
- Modificar conexión a base de datos en archivo *settings.py* 
Durante el desarrollo del sistema eliminar contenido dentro de ALLOWED_HOSTS y dejar DEBUG en True:
```
DEBUG = True
ALLOWED_HOSTS = []
```
Esto con el fin de que durante el desarrollo se pueda visualizar información detallada sobre los errores, durante producción o en el servidor en vivo, recuerda cambiar DEBUG por False, asi si tienes problemas se generará una página de error 500 o error 404 (que tiene su template) si es que la página no existe
- En cualquier parte durante la instalación si tienes dudas puedes consultar la [documentación de Django](https://docs.djangoproject.com/en/4.2/)
## Principales características

Este apartado del proyecto requiere un conocimiento básico de Django para comprender algunos conceptos claves de este framework

Dentro del proyecto principal llamado *scpApp* existe una App (reciclable) llamada *Rema* que la puedes identificar en los archivos encontrarás diversos archivos 
- *urls.py* que es para identificar la navegación entre páginas
- *forms.py* para la información relacionada a los formularios de cada centro de trabajo
- *views.py* será el archivo mas importante ya que dentro de el se encuentran todas las funciones principales, como el ingreso de información a la base de datos, previsualización y cálculo
- Una subcarpeta llamada *templates* que incluye archivos HTML para mostrar visualmente en el navegador la información de cada formulario o previsualizacion creada
- *models.py* Este archivo contiene la creación de modelos que representan las columnas y tablas de la base de datos creada, ¿Recuerdas que te mencioné que no era necesario tener las tablas en la base de datos creadas sino solo la base de datos?, Bien porque al tener esta información en el archivo *models.py* cuando se utilice *migrate* desde la linea de comandos, Django replicará lo que esta presente en el archivo models y creará las tablas que no esten creadas (en este caso todas, si ya creaste algunas Django solo creará las restantes por ejemplo las propias que requiere el framework para trabajar)

---
### Si necesitas crear una nueva área...

El sistema esta pensado para funcionar en el área de Remanufactura, aún no se implementa en el área de Tablero que es un objetivo secundario. Si necesitas crear una nueva área y sus centros de trabajos, tendrás que crear una [nueva App](https://docs.djangoproject.com/en/4.2/intro/tutorial01/) de Django


