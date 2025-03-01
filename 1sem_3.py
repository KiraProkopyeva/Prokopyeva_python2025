#прибавить 1 к числу [1, 2, 3] -> [1, 2, 4]

def plus_one(nums):
    for i in range (len(nums)-1, 0,-1):
        if nums[i] < 9:
            nums[i]+=1
            return nums
        else:
            nums[i] = 0
    return [1] + nums

print(plus_one([9, 0 ,9]))
