class Converter {
    static func celsiusToFahrenheit(c: Float64): Float64 {
        return (c * 1.8) + 32.0
    }
    static func fahrenheitToCelsius(f: Float64): Float64 {
        return (f - 32.0) / 1.8
    }
}

func findThreshold(start: Int64, target: Int64): Int64 {
    var i = start
    while (true) {
        if ((i * i) >= target) {
            return i
        }
        i += 1
    }

    0
}

main() {
    println("0C = ${Converter.celsiusToFahrenheit(0.0)}F")
    println("100C = ${Converter.celsiusToFahrenheit(100.0)}F")
    println("32F = ${Converter.fahrenheitToCelsius(32.0)}C")
    println("212F = ${Converter.fahrenheitToCelsius(212.0)}C")
    let t = findThreshold(1, 100)
    println("Threshold for 100: ${t}")
}
