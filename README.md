# Guía del proyecto

    1. Instalación de librerias, creación de entorno virtual y activación.
        pip install virtualenv
        virtualenv venv
        .venv\Scripts\activate
        pip install -r requirements.txt -- instalar las librerias
        pip freeze > requirements.txt -- actualizar la lista de librerias

    2. Creación de modulos
        python manage.py startapp nombre_del_modulo

    3. Creación de los modelos de la BD con el ORM de Django
        python manage.py makemigrations -- migración de las tablas
        python manage.py migrate -- creación de tablas en la BD

    
    4. Ejecución
        python manage.py runserver
        