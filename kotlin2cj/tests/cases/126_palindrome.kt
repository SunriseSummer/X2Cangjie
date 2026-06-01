// Palindrome checker
fun isPalindrome(s: String): Boolean {
    val chars = ArrayList<Char>()
    for (c in s) {
        chars.add(c)
    }
    var left = 0
    var right = chars.size - 1
    while (left < right) {
        if (chars[left] != chars[right]) return false
        left++
        right--
    }
    return true
}

fun longestPalindromicSubstring(s: String): String {
    val chars = ArrayList<Char>()
    for (c in s) {
        chars.add(c)
    }
    val n = chars.size
    if (n == 0) return ""
    var start = 0
    var maxLen = 1
    for (center in 0 until n) {
        // Odd length
        var lo = center
        var hi = center
        while (lo >= 0 && hi < n && chars[lo] == chars[hi]) {
            if (hi - lo + 1 > maxLen) {
                start = lo
                maxLen = hi - lo + 1
            }
            lo--
            hi++
        }
        // Even length
        lo = center
        hi = center + 1
        while (lo >= 0 && hi < n && chars[lo] == chars[hi]) {
            if (hi - lo + 1 > maxLen) {
                start = lo
                maxLen = hi - lo + 1
            }
            lo--
            hi++
        }
    }
    val result = ArrayList<Char>()
    for (i in start until start + maxLen) {
        result.add(chars[i])
    }
    val sb = StringBuilder()
    for (c in result) {
        sb.append(c)
    }
    return sb.toString()
}

fun main() {
    println("racecar: ${isPalindrome("racecar")}")
    println("hello: ${isPalindrome("hello")}")
    println("a: ${isPalindrome("a")}")
    println("Longest in babad: ${longestPalindromicSubstring("babad")}")
    println("Longest in cbbd: ${longestPalindromicSubstring("cbbd")}")
}
