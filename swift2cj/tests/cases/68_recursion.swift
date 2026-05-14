// Recursion + algorithmic: Fibonacci + greatest common divisor
func fib(_ n: Int) -> Int {
    if n < 2 { return n }
    return fib(n - 1) + fib(n - 2)
}

func gcd(_ a: Int, _ b: Int) -> Int {
    if b == 0 { return a }
    return gcd(b, a % b)
}

func factorial(_ n: Int) -> Int {
    var r = 1
    var i = 2
    while i <= n {
        r *= i
        i += 1
    }
    return r
}

func sumSquares(_ n: Int) -> Int {
    var s = 0
    for i in 1 ... n {
        s += i * i
    }
    return s
}

print(fib(0), fib(1), fib(2), fib(10), fib(15))
print(gcd(54, 24))
print(gcd(17, 5))
print(factorial(0), factorial(1), factorial(5), factorial(10))
print(sumSquares(5))
print(sumSquares(10))
