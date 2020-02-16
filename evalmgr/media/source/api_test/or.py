import math
from operator import xor
def countBits(number): 
    return int((math.log(number) / 
                math.log(2)) + 1);    


# Function to return the XOR of elements 
# from the range [1, n] 
def findXOR(n): 
	mod = n % 4; 

	# If n is a multiple of 4 
	if (mod == 0): 
		return n; 

	# If n % 4 gives remainder 1 
	elif (mod == 1): 
		return 1; 

	# If n % 4 gives remainder 2 
	elif (mod == 2): 
		return n + 1; 

	# If n % 4 gives remainder 3 
	elif (mod == 3): 
		return 0; 

# Function to return the XOR of elements 
# from the range [l, r] 
def findXORFun(l, r): 
	return (xor(findXOR(l - 1) , findXOR(r))); 
   
  
# Driver Code  
if __name__ == "__main__" : 
    t = int(input())
    for _ in range(t):
        a,b = [int(x) for x in input().split()]
        mod = 1000000007
        # L , R= a+1 ,b 
        xorr = findXORFun(a+1, b+1)
        xorr = xorr ^ a
        # lower = 2
        # upper = 6
        lower = countBits(a)
        upper = countBits(b+1)
        summ = a
        res = a
        if upper - lower <= 2:
            for i in range(a+1,b+1):
                summ = summ + (summ | i)
        else:
            low_limit = pow(2,lower)-1
            # print(low_limit)
            for i in range(a+1,low_limit):
                summ = summ + (summ | i)
            upper_limit = pow(2,upper-1)
            # print(upper_limit)
            for i in range(upper_limit,b+1):
                summ = summ + (summ | i)
            li = [x for x in range(lower+1,upper)]
            # print(li)
            temp = summ
            for i in range(len(li)-1):
                summ += pow(2,li[i]+li[i+1])
        print((summ+xorr)%mod)