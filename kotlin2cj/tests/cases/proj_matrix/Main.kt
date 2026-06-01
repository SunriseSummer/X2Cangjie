fun main() {
    val a = Matrix(2, 2)
    a.set(0, 0, 1); a.set(0, 1, 2)
    a.set(1, 0, 3); a.set(1, 1, 4)

    val b = Matrix(2, 2)
    b.set(0, 0, 5); b.set(0, 1, 6)
    b.set(1, 0, 7); b.set(1, 1, 8)

    println("Matrix A:")
    a.print()

    println("Matrix B:")
    b.print()

    println("A + B:")
    a.add(b).print()

    println("A * B:")
    a.multiply(b).print()

    println("Transpose A:")
    a.transpose().print()

    val c = Matrix(2, 3)
    c.set(0, 0, 1); c.set(0, 1, 2); c.set(0, 2, 3)
    c.set(1, 0, 4); c.set(1, 1, 5); c.set(1, 2, 6)

    val d = Matrix(3, 2)
    d.set(0, 0, 7); d.set(0, 1, 8)
    d.set(1, 0, 9); d.set(1, 1, 10)
    d.set(2, 0, 11); d.set(2, 1, 12)

    println("C (2x3):")
    c.print()

    println("D (3x2):")
    d.print()

    println("C * D:")
    c.multiply(d).print()
}
