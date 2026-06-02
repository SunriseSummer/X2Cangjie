class Counter {
    var count: Int64 = 0
    func increment() {
        count += 1
    }
    static func create(): Counter {
        return Counter()
    }
    static func createWithValue(initial: Int64): Counter {
        let c = Counter()
        var i = 0
        while (i < initial) {
            c.increment()
            i += 1
        }
        return c
    }
    func getCount(): Int64 {
        return count
    }
}

class MathHelper {
    static func square(x: Int64): Int64 {
        return x * x
    }
    static func cube(x: Int64): Int64 {
        return (x * x) * x
    }
    static func isEven(x: Int64): Bool {
        return (x % 2) == 0
    }
}

main() {
    let c1 = Counter.create()
    c1.increment()
    c1.increment()
    println("Counter1: ${c1.getCount()}")
    let c2 = Counter.createWithValue(5)
    println("Counter2: ${c2.getCount()}")
    println("Square of 4: ${MathHelper.square(4)}")
    println("Cube of 3: ${MathHelper.cube(3)}")
    println("Is 7 even? ${MathHelper.isEven(7)}")
    println("Is 8 even? ${MathHelper.isEven(8)}")
}
