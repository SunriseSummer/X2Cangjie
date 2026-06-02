import std.collection.*

func isPalindrome(s: String): Bool {
    let n = s.size
    for (i in 0..(n / 2)) {
        if (s.toRuneArray()[i] != s.toRuneArray()[(n - 1) - i]) {
            return false
        }
    }
    return true
}

func compress(s: String): String {
    if (s.isEmpty()) {
        return ""
    }
    let sb = StringBuilder()
    var count = 1
    for (i in 1..s.size) {
        if (s.toRuneArray()[i] == s.toRuneArray()[i - 1]) {
            count += 1
        } else {
            sb.append(s.toRuneArray()[i - 1])
            if (count > 1) {
                sb.append(count)
            }
            count = 1
        }
    }
    sb.append(s.toRuneArray()[s.size - 1])
    if (count > 1) {
        sb.append(count)
    }
    return sb.toString()
}

func reverseWords(s: String): String {
    let words = collectArrayList(s.split(" ").iterator())
    let result = ArrayList<String>()
    for (i in (words.size - 1)..=0 : -1) {
        if (!(words[i].isEmpty())) {
            result.add(words[i])
        }
    }
    return String.join(collectArray<String>(result.iterator().map({e => e.toString()})), delimiter: " ")
}

func countVowels(s: String): Int64 {
    var count = 0
    for (c in s.toAsciiLower().runes()) {
        if (((((c == r'a') || (c == r'e')) || (c == r'i')) || (c == r'o')) || (c == r'u')) {
            count += 1
        }
    }
    return count
}

main() {
    println(isPalindrome("racecar"))
    println(isPalindrome("hello"))
    println(isPalindrome("a"))
    println(isPalindrome(""))
    println(compress("aabcccccaaa"))
    println(compress("abc"))
    println(compress(""))
    println(reverseWords("hello world foo"))
    println(reverseWords("single"))
    println(countVowels("Hello World"))
    println(countVowels("xyz"))
    println(countVowels("aeiou"))
}
