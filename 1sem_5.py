def sum_two(mas, res):
    for i in range(len(mas)):
        for j in range(i, len(mas)):
            if mas[i] + mas[j] == res:
                return i, j

print(sum_two([1,2,3,4], 6))


def sum_two1(mas, res):
    a = dict()
    for i in range(len(mas)):
        if mas[i] in a:
            return i, a[mas[i]]
        a[res - mas[i]] = i

print(sum_two1([1,2,3,4], 6))    
