// String edge cases: empty strings, single chars, repeated operations
fun isPalindrome(s: String): Boolean {
    val n = s.length
    for (i in 0 until n / 2) {
        if (s[i] != s[n - 1 - i]) return false
    }
    return true
}

fun compress(s: String): String {
    if (s.isEmpty()) return ""
    val sb = StringBuilder()
    var count = 1
    for (i in 1 until s.length) {
        if (s[i] == s[i - 1]) {
            count++
        } else {
            sb.append(s[i - 1])
            if (count > 1) sb.append(count)
            count = 1
        }
    }
    sb.append(s[s.length - 1])
    if (count > 1) sb.append(count)
    return sb.toString()
}

fun reverseWords(s: String): String {
    val words = s.split(" ")
    val result = ArrayList<String>()
    for (i in words.size - 1 downTo 0) {
        if (words[i].isNotEmpty()) {
            result.add(words[i])
        }
    }
    return result.joinToString(" ")
}

fun countVowels(s: String): Int {
    var count = 0
    for (c in s.lowercase()) {
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
            count++
        }
    }
    return count
}

fun main() {
    // Palindrome tests
    println(isPalindrome("racecar"))
    println(isPalindrome("hello"))
    println(isPalindrome("a"))
    println(isPalindrome(""))

    // Compression
    println(compress("aabcccccaaa"))
    println(compress("abc"))
    println(compress(""))

    // Reverse words
    println(reverseWords("hello world foo"))
    println(reverseWords("single"))

    // Vowel counting
    println(countVowels("Hello World"))
    println(countVowels("xyz"))
    println(countVowels("aeiou"))
}
