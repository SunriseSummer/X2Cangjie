class Color(val r: Int, val g: Int, val b: Int) {
    companion object {
        fun red(): Color = Color(255, 0, 0)
        fun green(): Color = Color(0, 255, 0)
        fun blue(): Color = Color(0, 0, 255)
        fun white(): Color = Color(255, 255, 255)
        fun black(): Color = Color(0, 0, 0)
    }

    fun brightness(): Int = (r + g + b) / 3

    fun toHexPart(v: Int): String {
        val hi = v / 16
        val lo = v % 16
        return "${hexChar(hi)}${hexChar(lo)}"
    }

    fun hexChar(n: Int): String = when {
        n < 10 -> "$n"
        n == 10 -> "A"
        n == 11 -> "B"
        n == 12 -> "C"
        n == 13 -> "D"
        n == 14 -> "E"
        else -> "F"
    }

    fun toHex(): String = "#${toHexPart(r)}${toHexPart(g)}${toHexPart(b)}"

    fun describe(): String = "Color(r=$r, g=$g, b=$b, hex=${toHex()})"
}

class Converter {
    companion object {
        fun celsiusToFahrenheit(c: Int): Int = c * 9 / 5 + 32
        fun fahrenheitToCelsius(f: Int): Int = (f - 32) * 5 / 9
        fun kmToMiles(km: Int): Int = km * 621 / 1000
    }
}
