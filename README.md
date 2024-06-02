# Comandos úteis:

```
py -m venv venv
```
```
.\venv\Scripts\activate
```
```
pip install -r requirements.txt
```
```
py manage.py runserver
```
```
py manage.py createsuperuser
```
```
py manage.py makemigrations
```
```
py manage.py migrate
```


# Migrar de SQlite para DBeaver ( https://www.dio.me/articles/django-migrar-do-sqlite-para-postgresql )

## 1 - Antes de fazer a migração, certificar-se que não há nenhuma migração pendente.
````commandline
python manage.py makemigrations
python manage.py migrate
````


## 2 - Gerar um arquivo JSON que puxa os dados do atual banco de dados (ex: dumpdata.json)
```
python manage.py dumpdata > dumpdata.json
```


## 3 - Importante: mudar o encoding desse arquivo para UTF-8 (canto inferior direito no VSCode).


## 4 - Instalar o Psycopg2
```
pip install psycopg2
```

## 5 - Ir no settings.py do projeto e colocar os dados do bd:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'coordena_agora',
        'USER': 'postgres',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```

## 6 - Sincronizar o banco de dados
```
python manage.py migrate --run-syncdb
```

## 7 - Limpar os dados que vem no banco de dados por padrão
```
python manage.py shell
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
exit()
```

## 8 - Carregar os dados do arquivo JSON no banco de dados.
```
python manage.py loaddata dumpdata.json
```

## 9 - Checar no bd se migrou tudo certo.



# Comando para subir o redis (Web Socket):

docker run --rm -p 6379:6379 redis:7
