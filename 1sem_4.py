def number_of_unique_character(seq):
    res = {}
    for i in seq:
        res[i] = 1 + res.get(i, 0)

    return res

print(number_of_unique_character('aaahhhrowowow'))
