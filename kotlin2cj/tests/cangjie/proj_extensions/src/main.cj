package proj_extensions

import std.collection.*

extend Int64 {
    func isEven(): Bool {
        return (this % 2) == 0
    }
}

extend Int64 {
    func isOdd(): Bool {
        return (this % 2) != 0
    }
}

extend Int64 {
    func factorial(): Int64 {
        var result = 1
        var i = 1
        while (i <= this) {
            result *= i
            i += 1
        }
        return result
    }
}

extend String {
    func repeat(n: Int64): String {
        let sb = StringBuilder()
        var i = 0
        while (i < n) {
            sb.append(this)
            i += 1
        }
        return sb.toString()
    }
}

extend String {
    func countChar(target: String): Int64 {
        var count = 0
        var i = 0
        while (i < this.size) {
            if (this[i..i + 1] == target) {
                count += 1
            }
            i += 1
        }
        return count
    }
}

extend ArrayList<Int64> {
    func computeAvg(): Int64 {
        if (this.size == 0) {
            return 0
        }
        var sum = 0
        for (n in this) {
            sum += n
        }
        return sum / this.size
    }
}

main() {
    println("4 is even: ${4.isEven()}")
    println("7 is even: ${7.isEven()}")
    println("3 is odd: ${3.isOdd()}")
    println("8 is odd: ${8.isOdd()}")
    println("5! = ${5.factorial()}")
    println("0! = ${0.factorial()}")
    println("6! = ${6.factorial()}")
    println("'ab' * 3 = ${("ab" * 3)}")
    println("Count 'l' in 'hello world': ${"hello world".countChar("l")}")
    println("Count 'z' in 'hello': ${"hello".countChar("z")}")
    let nums = ArrayList([10, 20, 30, 40, 50])
    println("Average of [10,20,30,40,50]: ${nums.computeAvg()}")
    let empty = ArrayList<Int64>()
    println("Average of []: ${empty.computeAvg()}")
}