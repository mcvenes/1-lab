import requests
import json

# Тест для GET-запроса на получение текущего времени в Москве
def test_get_current_time():
    response = requests.get('http://localhost:8000?Europe/Moscow')
    assert response.status_code == 200  # Проверяем, что код ответа 200
    assert '<h1>Текущее время в Europe/Moscow</h1>' in response.text  # Проверяем, что в ответе есть заголовок

# Тест для GET-запроса на получение текущего времени в GMT
def test_get_current_time_gmt():
    response = requests.get('http://localhost:8000')
    assert response.status_code == 200  # Проверяем, что код ответа 200
    assert '<h1>Текущее время в GMT</h1>' in response.text  # Проверяем, что в ответе есть заголовок

# Тест для POST-запроса на преобразование времени
def test_post_convert_time():
    data = {'date': '12.20.2021 22:21:05', 'tz': 'EST'}  # Задаем данные для запроса
    response = requests.post('http://localhost:8000/api/v1/convert?target_tz=Europe/Moscow', json=data)  # Делаем POST-запрос
    assert response.status_code == 200  # Проверяем, что код ответа 200
    assert response.text == '2021-12-21 10:21:05'  # Проверяем, что время преобразовано верно

# Тест для POST-запроса на вычисление разницы в секундах
def test_post_datediff():
    data = {
        'first_date': '12.06.2024 22:21:05',
        'first_tz': 'EST',
        'second_date': '12:30pm 2024-02-01',
        'second_tz': 'Europe/Moscow'
    }  # Задаем данные для запроса
    response = requests.post('http://localhost:8000/api/v1/datediff', json=data)  # Делаем POST-запрос
    assert response.status_code == 200  # Проверяем, что код ответа 200
    # Проверяем, что разница в секундах верна с учетом возможных погрешностей времени
    assert abs(int(response.text) - 4572355) < 1000

# Запускаем тесты
if __name__ == '__main__':
    test_get_current_time()
    test_get_current_time_gmt()
    test_post_convert_time()
    test_post_datediff()
    print('Все тесты пройдены успешно!')