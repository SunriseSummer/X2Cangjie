func isPalindrome(s: String): Bool {
    let bytes = s.toArray()
    let n = bytes.size
    for (i in 0..n/2) {
        if (bytes[i] != bytes[n-1-i]) {
            return false
        }
    }
    return true
}

main() {
    println(isPalindrome("level"))
    println(isPalindrome("hello"))
    println(isPalindrome("racecar"))
    println(isPalindrome(""))
    return 0
}
