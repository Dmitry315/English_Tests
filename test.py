from requests import get, post

print(get('http://127.0.0.1:8000/user/1').json())
print(get('http://127.0.0.1:8000/users').json())
print(get('http://127.0.0.1:8000/test/3').json())
print(get('http://127.0.0.1:8000/test/theme/Present_Simple').json())