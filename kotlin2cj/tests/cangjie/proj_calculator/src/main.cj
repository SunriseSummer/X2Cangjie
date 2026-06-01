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

main() {
    let calc = Calculator()
    println("2 + 3 = ${calc.add(2, 3)}")
    println("10 - 4 = ${calc.subtract(10, 4)}")
    println("5 * 6 = ${calc.multiply(5, 6)}")
    println("15 / 3 = ${calc.divide(15, 3)}")
    println("10 / 0 = ${calc.divide(10, 0)}")
}