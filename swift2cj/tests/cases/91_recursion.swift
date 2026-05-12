// Small #1 (iter4): basic recursion (factorial / gcd / fibonacci)
func fact(_ n: Int) -> Int {
    if n <= 1 {
        return 1
    }
    return n * fact(n - 1)
}

func gcd(_ a: Int, _ b: Int) -> Int {
    if b == 0 {
        return a
    }
    return gcd(b, a % b)
}

func fib(_ n: Int) -> Int {
    if n < 2 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

print("5! = \(fact(5))")
print("10! = \(fact(10))")
print("gcd(48, 18) = \(gcd(48, 18))")
print("gcd(100, 75) = \(gcd(100, 75))")
print("fib(10) = \(fib(10))")
print("fib(15) = \(fib(15))")

// table of factorials
var i = 0
while i <= 8 {
    print("\(i)! = \(fact(i))")
    i += 1
}
