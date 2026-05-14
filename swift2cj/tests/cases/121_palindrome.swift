// Small #1 (iter8): numeric palindrome and digit reversal
func reverseNumber(_ n: Int) -> Int {
    var x = n
    var r = 0
    while x > 0 {
        r = r * 10 + (x % 10)
        x = x / 10
    }
    return r
}

func isPalindrome(_ n: Int) -> Bool {
    if n < 0 {
        return false
    }
    return n == reverseNumber(n)
}

let values = [0, 1, 7, 10, 11, 121, 1221, 12321, 12345, 1001]
for v in values {
    print("\(v): reverse=\(reverseNumber(v)) pal=\(isPalindrome(v))")
}
