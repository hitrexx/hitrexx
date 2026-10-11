N = int(input("Введите N: "))
array = []
min_ = float('inf')
for i in range(N):
    num = float(input(f"Введите array[{i}] элемент: "))
    array.append(num)
    if abs(num) < abs(min_):
        min_ = num
print(f"Минимальное по модулю число: {min_}")
print("Массив в обратном порядке: ", end=' ')
for i in reversed(range(0, N)):
    print(array[i], end=' ')
