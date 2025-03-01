#проверить последовательность скобок через стек

def brackets_chek(seq):
    stack = []
    for i in seq:
        stack = []
        if i == '(':
            stack.append(i)
        elif i == ')':
            if len(stack) == 0:
                return False
            stack.pop()
    return not stack

print(brackets_chek("(())"))
        
            
