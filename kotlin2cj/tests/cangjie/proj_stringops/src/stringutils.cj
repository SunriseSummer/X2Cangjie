package proj_stringops

class StringUtils {
    func reverseString(s: String): String {
        let sb = StringBuilder()
        var i = s.size - 1
        while (i >= 0) {
            sb.append(s.toRuneArray()[i])
            i -= 1
        }
        return sb.toString()
    }
    func countVowels(s: String): Int64 {
        var count = 0
        let lower = s.toAsciiLower()
        for (c in lower.runes()) {
            if (((((c == r'a') || (c == r'e')) || (c == r'i')) || (c == r'o')) || (c == r'u')) {
                count += 1
            }
        }
        return count
    }
    func isPalindrome(s: String): Bool {
        let cleaned = s.toAsciiLower()
        let reversed = reverseString(cleaned)
        return cleaned == reversed
    }
    func wordCount(s: String): Int64 {
        if (s.isEmpty()) {
            return 0
        }
        var count = 1
        for (c in s.runes()) {
            if (c == r' ') {
                count += 1
            }
        }
        return count
    }
    func capitalize(s: String): String {
        if (s.isEmpty()) {
            return s
        }
        let first = s[0..1].toAsciiUpper()
        if (s.size == 1) {
            return first
        }
        return first + s[1..]
    }
}
