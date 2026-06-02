import std.collection.*

func isPalindrome(s: String): Bool {
    let chars = ArrayList<Rune>()
    for (c in s.runes()) {
        chars.add(c)
    }
    var left = 0
    var right = chars.size - 1
    while (left < right) {
        if (chars[left] != chars[right]) {
            return false
        }
        left += 1
        right -= 1
    }
    return true
}

func longestPalindromicSubstring(s: String): String {
    let chars = ArrayList<Rune>()
    for (c in s.runes()) {
        chars.add(c)
    }
    let n = chars.size
    if (n == 0) {
        return ""
    }
    var start = 0
    var maxLen = 1
    for (center in 0..n) {
        var lo = center
        var hi = center
        while (((lo >= 0) && (hi < n)) && (chars[lo] == chars[hi])) {
            if (((hi - lo) + 1) > maxLen) {
                start = lo
                maxLen = (hi - lo) + 1
            }
            lo -= 1
            hi += 1
        }
        lo = center
        hi = center + 1
        while (((lo >= 0) && (hi < n)) && (chars[lo] == chars[hi])) {
            if (((hi - lo) + 1) > maxLen) {
                start = lo
                maxLen = (hi - lo) + 1
            }
            lo -= 1
            hi += 1
        }
    }
    let result = ArrayList<Rune>()
    for (i in start..(start + maxLen)) {
        result.add(chars[i])
    }
    let sb = StringBuilder()
    for (c in result) {
        sb.append(c)
    }
    return sb.toString()
}

main() {
    println("racecar: ${isPalindrome("racecar")}")
    println("hello: ${isPalindrome("hello")}")
    println("a: ${isPalindrome("a")}")
    println("Longest in babad: ${longestPalindromicSubstring("babad")}")
    println("Longest in cbbd: ${longestPalindromicSubstring("cbbd")}")
}
