from app.tasks.tasks import add

result = add.delay(41, 6)

print(result.id)
print(result.get())