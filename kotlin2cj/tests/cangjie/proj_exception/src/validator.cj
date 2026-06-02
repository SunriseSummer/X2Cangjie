package proj_exception

class Validator {
    func validateAge(age: Int64): String {
        if (age < 0) {
            throw IllegalArgumentException("Age cannot be negative: ${age}")
        }
        if (age > 150) {
            throw IllegalArgumentException("Age too large: ${age}")
        }
        return "Valid age: ${age}"
    }
    func validateName(name: String): String {
        if (name.isEmpty()) {
            throw IllegalArgumentException("Name cannot be empty")
        }
        return "Valid name: ${name}"
    }
    func safeDivide(a: Int64, b: Int64): String {
        return try {
            if (b == 0) {
                throw ArithmeticException("Division by zero")
            }
            "Result: ${a / b}"
        } catch (e: ArithmeticException) {
            "Error: ${e.message}"
        }
    }
    func parseNumber(s: String): Int64 {
        var result = 0
        var negative = false
        var i = 0
        if (s.isEmpty()) {
            throw IllegalArgumentException("Empty string")
        }
        if (s.toRuneArray()[0] == r'-') {
            negative = true
            i = 1
        }
        while (i < s.size) {
            let c = s.toRuneArray()[i]
            if ((c < r'0') || (c > r'9')) {
                throw IllegalArgumentException("Invalid char: ${c}")
            }
            result = (result * 10) + ((Int64(UInt32(c)) - Int64(UInt32(r'0'))))
            i += 1
        }
        return if (negative) {
            -result
        } else {
            result
        }
    }
}
