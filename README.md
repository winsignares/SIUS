# Guía para la instalación del proyecto

    1. Instalación de librerias, creación de entorno virtual y activación.
        pip install virtualenv
        virtualenv venv
        venv\Scripts\activate.bat
        pip install -r requirements.txt -- instalar las librerias
        pip freeze > requirements.txt -- actualizar la lista de librerias
        
    2. Creación de la carpeta del proyecto
        django-admin startproject siuc .

    3. Creación de modulos
        python manage.py startapp login

















    Base de datos
        pip install psycopg2
