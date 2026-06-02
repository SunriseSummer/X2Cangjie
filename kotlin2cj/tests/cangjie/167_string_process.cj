import std.collection.*

func isValidEmail(email: String): Bool {
    let atIndex = (email.indexOf("@") ?? -1)
    if ((atIndex <= 0) || (atIndex >= (email.size - 1))) {
        return false
    }
    let domain = email[atIndex + 1..]
    if ((domain.indexOf(".") ?? -1) <= 0) {
        return false
    }
    return true
}

func caesarEncrypt(text: String, shift: Int64): String {
    let sb = StringBuilder()
    for (c in text.runes()) {
        if (c >= r'A' && c <= r'Z') {
            sb.append(Rune(UInt32(((((Int64(UInt32(c)) - 65) + shift) % 26) + 65))))
        } else if (c >= r'a' && c <= r'z') {
            sb.append(Rune(UInt32(((((Int64(UInt32(c)) - 97) + shift) % 26) + 97))))
        } else {
            sb.append(c)
        }
    }
    return sb.toString()
}

func countVowels(s: String): Int64 {
    var count = 0
    for (c in s.runes()) {
        if ((((((((((c == r'a') || (c == r'e')) || (c == r'i')) || (c == r'o')) || (c == r'u')) || (c == r'A')) || (c == r'E')) || (c == r'I')) || (c == r'O')) || (c == r'U')) {
            count += 1
        }
    }
    return count
}

func reverseWords(s: String): String {
    let words = collectArrayList(s.split(" ").iterator())
    let result = ArrayList<String>()
    for (i in (words.size - 1)..=0 : -1) {
        result.add(words[i])
    }
    let sb = StringBuilder()
    for (i in 0..=(result.size - 1)) {
        if (i > 0) {
            sb.append(" ")
        }
        sb.append(result[i])
    }
    return sb.toString()
}

main() {
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
