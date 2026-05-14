// Small #2 (iter5): palindrome / digit reverse / digit sum on integers
func reverseDigits(_ n: Int) -> Int {
    var x = n
    var r = 0
    while x > 0 {
        r = r * 10 + (x % 10)
        x = x / 10
    }
    return r
}

func isPalindrome(_ n: Int) -> Bool {
    return n == reverseDigits(n)
}

func digitSum(_ n: Int) -> Int {
    var x = n
    var s = 0
    while x > 0 {
        s += x % 10
        x = x / 10
    }
    return s
}

func digitalRoot(_ n: Int) -> Int {
    var x = n
    while x >= 10 {
        x = digitSum(x)
    }
    return x
}

for v in [121, 123, 909, 1234, 1221, 99] {
    print("\(v): reverse=\(reverseDigits(v)) palin=\(isPalindrome(v)) sum=\(digitSum(v)) root=\(digitalRoot(v))")
}

print("--- range scan 100..120 for palindromes ---")
var k = 100
while k <= 120 {
    if isPalindrome(k) {
        print("palindrome: \(k)")
    }
    k += 1
}
