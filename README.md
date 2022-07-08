# Proyecto IS2
## Integrantes
- Álvaro Castillo
- Marcel Gutiérrez
- Milenko Bonacich
- Franco Carrión
- Mauricio Furniel
---
## Proyecto:
> El producto a implementar consistirá de una página web de inicio para los administradores donde deben iniciar sesión con su usuario(correo de la empresa) y clave. Una vez dentro, tendrán la capacidad de crear, editar y eliminar encuestas pertenecientes a su empresa, las cuales una vez terminadas podrán enviar a una lista de correos electrónicos almacenados en una base de datos, el administrador podrá ver las respuestas de estas encuestas descritas de forma gráfica. 
La interacción de los encuestados con la página comenzará desde el correo electrónico, donde todos reciben la misma url de la encuesta ej: “primera encuesta” y una url diferente para cada nueva encuesta. Entrando a la url podrán acceder y responder la encuesta correspondiente y visualizar las respuestas de una forma similar al administrador.

---
## Detalles del proyecto:
> El proyecto está implementado en python haciendo uso del framework flask y para la estilización del proyecto se hizo uso de la biblioteca bootstrap.
> El proyecto hace uso de una base de datos sql en la nube de la plataforma heroku, si se quiere usar otra base de datos se tiene que cambiar los datos de la función `get_dbconnection()` ubicada en el archivo `app/__init__.py` y tiene que tener la siguiente estructura:
### Estructura de la Base de datos
- `encuesta`:
	- `id_e varchar`: Id de la encuesta, clave primaria
	- `titulo varchar`: Título de la encuesta
	- `f_ini date`: Fecha de inicio de la encuesta.
	- `f_exp date`: Fecha de expiración de la encuesta.
	- - `descripcion varchar`: Descripción de la encuesta.
- `pregunta`
	- `id_p varchar`: Id de la pregunta, clave primaria
	- `id_e varchar`: Id de la encuesta a la que corresponde, clave foránea a `encuesta`
	- `texto varchar`: Texto de la pregunta mostrado en la encuesta.
- `alternativa`
	- `id_a varchar`: Id de alternativa, clave primaria
	- `id_p varchar`: Id de la pregunta a la que corresponde, clave foránea a `pregunta`
	- `texto varchar`: Texto de la alternativa mostrado en la pregunta.
	- `cont_r int`: Contador de quiénes han respondido la encuesta.
- `email`:
	- `id varchar`: Tiene que ser un email o puede causar comportamiento inesperado, clave primaria.
- `respondido`:
	- `email varchar`: Email del encuestado, clave foránea a `email`
	- `id_e varchar`: Id de la encuesta a responder, clave foránea a `encuesta`
	- `hash varchar`: Hash generado de la concatenación de `email` y `id_e` para un url único
	- `respondido bool`: Booleano para saber si se ha respondido la encuesta o no
- `usuario`:
	- `username varchar`: Tiene que ser un email o puede que el usuario no sea accesible por el programa
	- `password varchar`: Hash de la contraseña del usuario
	- `nick varchar`: Apodo del usuario.
### Dependencias Principales:
- `prototipos/`: Prototipos para integración
	- `IS2_Marcel/`: Prototipo de registro y lista de emails
	- `listaRespuestas/`: Prototipo de visualización de conteo de respuestas
	- `responder/`: Prototipo de interfaz de encuestado
	- `t1_milenko/`: Prototipo de creación de encuestas
	- `palMile/`: Prototipo de ejemplo para creación de
- `entregable/`: Producto entregable del sprint 3
	- `app`: Directorio con archivos principales del proyecto
		- `__init__.py`: Archivo con todos los imports del proyecto, funciones y variables globales
		- `*_views.py`: Archivos con la lógica referente a las rutas del proyecto
		- `templates/`: Archivos .html
		- `static/`: Archivos .css e imágenes

### Ejemplo Ejecución:
> El proyecto es ejecutable desde `/entregable/run.py` usando el comando `python run.py`, al ingresar, se puede entrar a la vista de administrador con la cuenta alvaro@encuestas.cl y contraseña pass123
> IMPORTANTE: no usar flask run o porcentaje del código (`if __name__ == "__main__"`) no se ejecutará, por lo que tendrá un comportamiento inesperado