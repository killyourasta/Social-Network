# yatube_project

Социальная сеть блогеров

## Выполнила работу Галиева Ляйсан

Разворачивание проекта:

Клонировать репозиторий и перейти в его папку в командной строке:

git clone
Cоздать и активировать виртуальное окружение:

python3 -m venv venv
Для *nix-систем и MacOS:

source venv/bin/activate
Для windows-систем:

source venv/Scripts/activate
Установить зависимости из файла requirements.txt:

pip install -r requirements.txt
Выполнить миграции:

python3 manage.py migrate
Запустить проект:

python3 manage.py runserver
Создать суперпользователя Django:

python3 manage.py createsuperuser
Сам проект и админ-панель по адресам:

http://127.0.0.1:8000

http://127.0.0.1:8000/admin


