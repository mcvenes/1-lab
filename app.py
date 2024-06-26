from datetime import datetime
from wsgiref.simple_server import make_server
from tzlocal import get_localzone
from pytz import timezone
import json  # Импортируем библиотеку для работы с JSON

# Определяем функцию приложения, которая обрабатывает запросы
def application(environ, start_response):
    # Извлекаем путь запроса и метод HTTP
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    # Обрабатываем GET-запросы
    if method == 'GET':
        # Если запрос на корневой путь, выводим текущее время в заданной зоне
        if path == '/':
            # Получаем имя временной зоны из строки запроса
            tz_name = environ.get('QUERY_STRING')
            # Получаем текущее время
            current_time = get_current_time(tz_name)
            # Отправляем ответ клиенту с кодом 200 OK
            start_response('200 OK', [('Content-type', 'text/html')])
            # Возвращаем HTML-ответ с текущим временем
            return [f'<h1>The current time in {tz_name or "GMT"}:</h1><p>{current_time}</p>'.encode()]
        # Если запрос на другой путь, отправляем ошибку 404
        else:
            start_response('404 Not Found', [('Content-type', 'text/html')])
            return [b'<h1>404 Not Found</h1>']

    # Обрабатываем POST-запросы
    elif method == 'POST':
        # Если запрос на /api/v1/convert, преобразуем время из одной зоны в другую
        if path == '/api/v1/convert':
            try:
                # Читаем тело запроса
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                request_body = environ['wsgi.input'].read(request_body_size).decode()
                # Декодируем JSON-данные из тела запроса
                data = json.loads(request_body)
                # Извлекаем дату, исходную зону и целевую зону
                date = data['date']
                tz = data['tz']
                target_tz = environ['QUERY_STRING']
                # Преобразуем время
                converted_time = convert_time(date, tz, target_tz)
                # Отправляем ответ клиенту с кодом 200 OK
                start_response('200 OK', [('Content-type', 'text/plain')])
                # Возвращаем преобразованное время
                return [f'{converted_time}'.encode()]
            # Обрабатываем ошибки
            except Exception as e:
                start_response('400 Bad Request', [('Content-type', 'text/plain')])
                return [f'Error: {str(e)}'.encode()]

        # Если запрос на /api/v1/datediff, вычисляем разницу в секундах между двумя датами
        elif path == '/api/v1/datediff':
            try:
                # Читаем тело запроса
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                request_body = environ['wsgi.input'].read(request_body_size).decode()
                # Декодируем JSON-данные из тела запроса
                data = json.loads(request_body)
                # Извлекаем даты и зоны
                first_date = data['first_date']
                first_tz = data['first_tz']
                second_date = data['second_date']
                second_tz = data['second_tz']
                # Вычисляем разницу в секундах
                seconds_diff = calculate_seconds_diff(first_date, first_tz, second_date, second_tz)
                # Отправляем ответ клиенту с кодом 200 OK
                start_response('200 OK', [('Content-type', 'text/plain')])
                # Возвращаем разницу в секундах
                return [f'{seconds_diff}'.encode()]
            # Обрабатываем ошибки
            except Exception as e:
                start_response('400 Bad Request', [('Content-type', 'text/plain')])
                return [f'Error: {str(e)}'.encode()]

        # Если запрос на другой путь, отправляем ошибку 404
        else:
            start_response('404 Not Found', [('Content-type', 'text/html')])
            return [b'<h1>404 Not Found</h1>']

    # Если запрос не GET или POST, отправляем ошибку 405
    else:
        start_response('405 Method Not Allowed', [('Content-type', 'text/html')])
        return [b'<h1>405 Method Not Allowed</h1>']


# Функция для получения текущего времени в заданной зоне
def get_current_time(tz_name):
    # Получаем объект временной зоны
    tz = timezone(tz_name) if tz_name else get_localzone()
    # Получаем текущее время в заданной зоне
    current_time = datetime.now(tz)
    # Форматируем время в строку
    return current_time.strftime('%Y-%m-%d %H:%M:%S')

# Функция для преобразования времени из одной зоны в другую
def convert_time(date_str, tz, target_tz):
    # Преобразуем строку даты в объект datetime
    datetime_obj = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
    # Получаем объекты временных зон
    source_tz = timezone(tz)
    target_tz = timezone(target_tz)
    # Преобразуем время в целевую зону
    converted_time = datetime_obj.replace(tzinfo=source_tz).astimezone(target_tz)
    # Форматируем время в строку
    return converted_time.strftime('%Y-%m-%d %H:%M:%S')

# Функция для вычисления разницы в секундах между двумя датами
def calculate_seconds_diff(first_date, first_tz, second_date, second_tz):
    # Преобразуем строки дат в объекты datetime
    first_datetime = datetime.strptime(first_date, '%m.%d.%Y %H:%M:%S')
    second_datetime = datetime.strptime(second_date, '%I:%M%p %Y-%m-%d')
    # Получаем объекты временных зон
    first_tz = timezone(first_tz)
    second_tz = timezone(second_tz)
    # Устанавливаем временные зоны для объектов datetime
    first_datetime = first_datetime.replace(tzinfo=first_tz)
    second_datetime = second_datetime.replace(tzinfo=second_tz)
    # Вычисляем разницу в секундах
    seconds_diff = (second_datetime - first_datetime).total_seconds()
    # Возвращаем результат
    return int(seconds_diff)

# Запускаем сервер
if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()