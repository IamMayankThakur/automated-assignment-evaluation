a = 2
b = 6
import math
def countBits(number): 
    return int((math.log(number) / 
                math.log(2)) + 1);    
lower = countBits(a)
upper = countBits(b+1)
# lower = 2
# upper = 6
summ = a
if upper - lower <= 2:
    for i in range(a+1,b+1):
        summ = summ + (summ | i)
else:
    low_limit = pow(2,lower)-1
    print(low_limit)
    for i in range(a+1,low_limit):
        summ = summ + (summ | i)
    upper_limit = pow(2,upper-1)
    print(upper_limit)
    for i in range(upper_limit,b+1):
        summ = summ + (summ | i)
    li = [x for x in range(lower+1,upper)]
    print(li)
    temp = summ
    for i in range(len(li)-1):
        summ += pow(2,li[i]+li[i+1])
print(summ)
        # temp_sum = pow(2,i+i+1)