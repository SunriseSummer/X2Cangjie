fun main() {
    val r = Color.red()
    val g = Color.green()
    val b = Color.blue()
    val w = Color.white()
    val k = Color.black()

    println(r.describe())
    println(g.describe())
    println(b.describe())
    println(w.describe())
    println(k.describe())

    println("Red brightness: ${r.brightness()}")
    println("White brightness: ${w.brightness()}")
    println("Black brightness: ${k.brightness()}")

    println("100C = ${Converter.celsiusToFahrenheit(100)}F")
    println("32F = ${Converter.fahrenheitToCelsius(32)}C")
    println("0C = ${Converter.celsiusToFahrenheit(0)}F")
    println("10km = ${Converter.kmToMiles(10)} miles")
}
