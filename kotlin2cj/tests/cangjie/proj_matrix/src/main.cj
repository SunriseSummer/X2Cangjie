package proj_matrix

import std.collection.*

class Matrix {
    let rows: Int64
    let cols: Int64
    init(rows: Int64, cols: Int64) {
        this.rows = rows
        this.cols = cols
        for (i in 0..rows) {
            let row = ArrayList<Int64>()
            for (j in 0..cols) {
                row.add(0)
            }
            data.add(row)
        }
    }
    let data = ArrayList<ArrayList<Int64>>()
    func set(r: Int64, c: Int64, value: Int64) {
        data[r][c] = value
    }
    func get(r: Int64, c: Int64): Int64 {
        return data[r][c]
    }
    func add(other: Matrix): Matrix {
        let result = Matrix(rows, cols)
        for (i in 0..rows) {
            for (j in 0..cols) {
                result.set(i, j, get(i, j) + other.get(i, j))
            }
        }
        return result
    }
    func multiply(other: Matrix): Matrix {
        let result = Matrix(rows, other.cols)
        for (i in 0..rows) {
            for (j in 0..other.cols) {
                var sum = 0
                for (k in 0..cols) {
                    sum += get(i, k) * other.get(k, j)
                }
                result.set(i, j, sum)
            }
        }
        return result
    }
    func transpose(): Matrix {
        let result = Matrix(cols, rows)
        for (i in 0..rows) {
            for (j in 0..cols) {
                result.set(j, i, get(i, j))
            }
        }
        return result
    }
    func print() {
        for (i in 0..rows) {
            let sb = StringBuilder()
            for (j in 0..cols) {
                if (j > 0) {
                    sb.append(" ")
                }
                sb.append(get(i, j))
            }
            println(sb.toString())
        }
    }
}

main() {
    let a = Matrix(2, 2)
    a.set(0, 0, 1)
    a.set(0, 1, 2)
    a.set(1, 0, 3)
    a.set(1, 1, 4)
    let b = Matrix(2, 2)
    b.set(0, 0, 5)
    b.set(0, 1, 6)
    b.set(1, 0, 7)
    b.set(1, 1, 8)
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
    let c = Matrix(2, 3)
    c.set(0, 0, 1)
    c.set(0, 1, 2)
    c.set(0, 2, 3)
    c.set(1, 0, 4)
    c.set(1, 1, 5)
    c.set(1, 2, 6)
    let d = Matrix(3, 2)
    d.set(0, 0, 7)
    d.set(0, 1, 8)
    d.set(1, 0, 9)
    d.set(1, 1, 10)
    d.set(2, 0, 11)
    d.set(2, 1, 12)
    println("C (2x3):")
    c.print()
    println("D (3x2):")
    d.print()
    println("C * D:")
    c.multiply(d).print()
}