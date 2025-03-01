#фибоначчи 1 способ

def fib(n):
    prev = 0
    curr = 1
    
    if n == 0: return 0
    
    for i in range(n-1):
        temp = curr
        curr += prev
        prev = temp

    return curr

print(fib(5))

#фибоначчи 2 способ

def fib(n):
    if n == 0: return 0
    if n == 1: return 1

    return fib(n-1) + fib(n-2)

print(fib(5))
    
    
