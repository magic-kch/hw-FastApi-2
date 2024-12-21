import requests

# response = requests.post( "http://127.0.0.1:8000/api/v1/user", json={
#     "name": "user_2",
#     "password": "1234"
# }
#                           )
# print(response.status_code)
# print(response.json())

response = requests.post( "http://127.0.0.1:8080/login", json={
  "name": "test_user_1",
  "email": "user1@test.ru",
  "password": "123456789Qwerty"
}
                          )
print(response.status_code)
print(response.json())
token = response.json()["token"]

response = requests.post(
    "http://127.0.0.1:8080/advertisement",
    json={
  "title": "Магнитафон 5000",
  "description": "супер мафон",
  "price": 1000
},
    headers={"x-token": token}
)
print(response.json())
todo_id = response.json()["id"]

# response = requests.patch(
#     f"http://127.0.0.1:8000/api/v1/todo/1", json={"done": True},
#     headers={'x-token': token}
# )
#
# print(response.status_code)
# print(response.json())

# response = requests.get(
#     f"http://127.0.0.1:8000/api/v1/todo/1",
# )
#
# print(response.json())

