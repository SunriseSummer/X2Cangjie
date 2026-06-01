// Number-to-Roman and Roman-to-Number conversion
fun intToRoman(num: Int): String {
    val values = arrayListOf(1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    val symbols = arrayListOf("M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I")
    var result = ""
    var n = num
    for (i in 0 until values.size) {
        while (n >= values[i]) {
            result += symbols[i]
            n -= values[i]
        }
    }
    return result
}

fun romanToInt(s: String): Int {
    val map = HashMap<Char, Int>()
    map['I'] = 1
    map['V'] = 5
    map['X'] = 10
    map['L'] = 50
    map['C'] = 100
    map['D'] = 500
    map['M'] = 1000
    var result = 0
    for (i in 0 until s.length) {
        val cur = map[s[i]]!!
        if (i + 1 < s.length && cur < map[s[i + 1]]!!) {
            result -= cur
        } else {
            result += cur
        }
    }
    return result
}

fun main() {
    println("3749 -> ${intToRoman(3749)}")
    println("58 -> ${intToRoman(58)}")
    println("1994 -> ${intToRoman(1994)}")
    println("MCMXCIV -> ${romanToInt("MCMXCIV")}")
    println("LVIII -> ${romanToInt("LVIII")}")
    println("IX -> ${romanToInt("IX")}")
}
