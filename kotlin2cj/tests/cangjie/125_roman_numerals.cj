import std.collection.*

func intToRoman(num: Int64): String {
    let values = ArrayList([1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1])
    let symbols = ArrayList(["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"])
    var result = ""
    var n = num
    for (i in 0..values.size) {
        while (n >= values[i]) {
            result += symbols[i].toString()
            n -= values[i]
        }
    }
    return result
}

func romanToInt(s: String): Int64 {
    let map = HashMap<Rune, Int64>()
    map[r'I'] = 1
    map[r'V'] = 5
    map[r'X'] = 10
    map[r'L'] = 50
    map[r'C'] = 100
    map[r'D'] = 500
    map[r'M'] = 1000
    var result = 0
    for (i in 0..s.size) {
        let cur = map[s.toRuneArray()[i]]
        if (((i + 1) < s.size) && (cur < map[s.toRuneArray()[i + 1]])) {
            result -= cur
        } else {
            result += cur
        }
    }
    return result
}

main() {
    println("3749 -> ${intToRoman(3749)}")
    println("58 -> ${intToRoman(58)}")
    println("1994 -> ${intToRoman(1994)}")
    println("MCMXCIV -> ${romanToInt("MCMXCIV")}")
    println("LVIII -> ${romanToInt("LVIII")}")
    println("IX -> ${romanToInt("IX")}")
}
