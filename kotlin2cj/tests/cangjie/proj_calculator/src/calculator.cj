package proj_calculator

class Calculator {
    func add(a: Int64, b: Int64): Int64 {
        return a + b
    }
    func subtract(a: Int64, b: Int64): Int64 {
        return a - b
    }
    func multiply(a: Int64, b: Int64): Int64 {
        return a * b
    }
    func divide(a: Int64, b: Int64): Int64 {
        if (b == 0) {
            println("Error: division by zero")
            return 0
        }
        return a / b
    }
}
