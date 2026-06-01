class StringUtils {
    fun reverseString(s: String): String {
        val sb = StringBuilder()
        var i = s.length - 1
        while (i >= 0) {
            sb.append(s[i])
            i--
        }
        return sb.toString()
    }

    fun countVowels(s: String): Int {
        var count = 0
        val lower = s.lowercase()
        for (c in lower) {
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
                count++
            }
        }
        return count
    }

    fun isPalindrome(s: String): Boolean {
        val cleaned = s.lowercase()
        val reversed = reverseString(cleaned)
        return cleaned == reversed
    }

    fun wordCount(s: String): Int {
        if (s.isEmpty()) return 0
        var count = 1
        for (c in s) {
            if (c == ' ') count++
        }
        return count
    }

    fun capitalize(s: String): String {
        if (s.isEmpty()) return s
        val first = s.substring(0, 1).uppercase()
        if (s.length == 1) return first
        return first + s.substring(1)
    }
}
