// Test: String processing intensive - parsing, validation, transformation
fun isValidEmail(email: String): Boolean {
    val atIndex = email.indexOf("@")
    if (atIndex <= 0 || atIndex >= email.length - 1) return false
    val domain = email.substring(atIndex + 1)
    if (domain.indexOf(".") <= 0) return false
    return true
}

fun caesarEncrypt(text: String, shift: Int): String {
    val sb = StringBuilder()
    for (c in text) {
        if (c in 'A'..'Z') {
            sb.append(((c.code - 65 + shift) % 26 + 65).toChar())
        } else if (c in 'a'..'z') {
            sb.append(((c.code - 97 + shift) % 26 + 97).toChar())
        } else {
            sb.append(c)
        }
    }
    return sb.toString()
}

fun countVowels(s: String): Int {
    var count = 0
    for (c in s) {
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
            c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
            count++
        }
    }
    return count
}

fun reverseWords(s: String): String {
    val words = s.split(" ")
    val result = ArrayList<String>()
    for (i in words.size - 1 downTo 0) {
        result.add(words[i])
    }
    val sb = StringBuilder()
    for (i in 0..result.size - 1) {
        if (i > 0) sb.append(" ")
        sb.append(result[i])
    }
    return sb.toString()
}

fun main() {
    println(isValidEmail("user@example.com"))
    println(isValidEmail("invalid"))
    println(isValidEmail("@no.com"))
    println(isValidEmail("a@b"))

    println(caesarEncrypt("Hello World", 3))
    println(caesarEncrypt("Khoor Zruog", 23))

    println(countVowels("Hello World"))
    println(countVowels("xyz"))

    println(reverseWords("the quick brown fox"))
}
