package proj_calculator

main() {
    let calc = Calculator()
    println("2 + 3 = ${calc.add(2, 3)}")
    println("10 - 4 = ${calc.subtract(10, 4)}")
    println("5 * 6 = ${calc.multiply(5, 6)}")
    println("15 / 3 = ${calc.divide(15, 3)}")
    println("10 / 0 = ${calc.divide(10, 0)}")
}
