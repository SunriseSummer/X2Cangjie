package proj_companion

class Color {
    let r: Int64
    let g: Int64
    let b: Int64
    init(r: Int64, g: Int64, b: Int64) {
        this.r = r
        this.g = g
        this.b = b
    }
    static func red(): Color {
        return Color(255, 0, 0)
    }
    static func green(): Color {
        return Color(0, 255, 0)
    }
    static func blue(): Color {
        return Color(0, 0, 255)
    }
    static func white(): Color {
        return Color(255, 255, 255)
    }
    static func black(): Color {
        return Color(0, 0, 0)
    }
    func brightness(): Int64 {
        return ((r + g) + b) / 3
    }
    func toHexPart(v: Int64): String {
        let hi = v / 16
        let lo = v % 16
        return "${hexChar(hi)}${hexChar(lo)}"
    }
    func hexChar(n: Int64): String {
        return if (n < 10) {
            "${n}"
        } else if (n == 10) {
            "A"
        } else if (n == 11) {
            "B"
        } else if (n == 12) {
            "C"
        } else if (n == 13) {
            "D"
        } else if (n == 14) {
            "E"
        } else {
            "F"
        }
    }
    func toHex(): String {
        return "#${toHexPart(r)}${toHexPart(g)}${toHexPart(b)}"
    }
    func describe(): String {
        return "Color(r=${r}, g=${g}, b=${b}, hex=${toHex()})"
    }
}

class Converter {
    static func celsiusToFahrenheit(c: Int64): Int64 {
        return ((c * 9) / 5) + 32
    }
    static func fahrenheitToCelsius(f: Int64): Int64 {
        return ((f - 32) * 5) / 9
    }
    static func kmToMiles(km: Int64): Int64 {
        return (km * 621) / 1000
    }
}
