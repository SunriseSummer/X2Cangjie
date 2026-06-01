// Test: companion object and while(true) combined
class Converter {
    companion object {
        fun celsiusToFahrenheit(c: Double): Double = c * 1.8 + 32.0
        fun fahrenheitToCelsius(f: Double): Double = (f - 32.0) / 1.8
    }
}

fun findThreshold(start: Int, target: Int): Int {
    var i = start
    while (true) {
        if (i * i >= target) return i
        i++
    }
}

fun main() {
    println("0C = ${Converter.celsiusToFahrenheit(0.0)}F")
    println("100C = ${Converter.celsiusToFahrenheit(100.0)}F")
    println("32F = ${Converter.fahrenheitToCelsius(32.0)}C")
    println("212F = ${Converter.fahrenheitToCelsius(212.0)}C")

    val t = findThreshold(1, 100)
    println("Threshold for 100: $t")
}
