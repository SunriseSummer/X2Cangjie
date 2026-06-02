class Validator {
    fun validateAge(age: Int): String {
        if (age < 0) {
            throw IllegalArgumentException("Age cannot be negative: $age")
        }
        if (age > 150) {
            throw IllegalArgumentException("Age too large: $age")
        }
        return "Valid age: $age"
    }

    fun validateName(name: String): String {
        if (name.isEmpty()) {
            throw IllegalArgumentException("Name cannot be empty")
        }
        return "Valid name: $name"
    }

    fun safeDivide(a: Int, b: Int): String {
        return try {
            if (b == 0) {
                throw ArithmeticException("Division by zero")
            }
            "Result: ${a / b}"
        } catch (e: ArithmeticException) {
            "Error: ${e.message}"
        }
    }

    fun parseNumber(s: String): Int {
        var result = 0
        var negative = false
        var i = 0
        if (s.isEmpty()) {
            throw IllegalArgumentException("Empty string")
        }
        if (s[0] == '-') {
            negative = true
            i = 1
        }
        while (i < s.length) {
            val c = s[i]
            if (c < '0' || c > '9') {
                throw IllegalArgumentException("Invalid char: $c")
            }
            result = result * 10 + (c - '0')
            i++
        }
        return if (negative) -result else result
    }
}
