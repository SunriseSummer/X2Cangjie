// Test: Companion object support
class Counter {
    var count: Int = 0

    fun increment() {
        count++
    }

    companion object {
        fun create(): Counter {
            return Counter()
        }

        fun createWithValue(initial: Int): Counter {
            val c = Counter()
            var i = 0
            while (i < initial) {
                c.increment()
                i++
            }
            return c
        }
    }

    fun getCount(): Int = count
}

class MathHelper {
    companion object {
        fun square(x: Int): Int = x * x
        fun cube(x: Int): Int = x * x * x
        fun isEven(x: Int): Boolean = x % 2 == 0
    }
}

fun main() {
    val c1 = Counter.create()
    c1.increment()
    c1.increment()
    println("Counter1: ${c1.getCount()}")

    val c2 = Counter.createWithValue(5)
    println("Counter2: ${c2.getCount()}")

    println("Square of 4: ${MathHelper.square(4)}")
    println("Cube of 3: ${MathHelper.cube(3)}")
    println("Is 7 even? ${MathHelper.isEven(7)}")
    println("Is 8 even? ${MathHelper.isEven(8)}")
}
