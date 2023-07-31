import math

def isPrime(n):
  for i in range(2,int(math.sqrt(n))+1):
    if (n%i) == 0:
      return False
  return True

def nearestPrime(x):
    if( not isinstance(x, int) or not isinstance(x, float) ):
        print("Error: Input can only be a single scalar or float")
        exit

    if( isPrime( math.floor(x) ) ):
        return math.floor(x)
    elif( isPrime( math.ceil(x) ) ):
        return math.ceil(x)

    tmp = [math.ceil(x), math.floor(x)]

    while( not (isPrime(tmp[0]) or isPrime(tmp[1])) ):
        tmp = [tmp[0]-1, tmp[1]+1]

    if(isPrime(tmp[0])):
        return tmp[0]
    else:
        return tmp[1]        