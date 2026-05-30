fun main() {
    var s = 0
    for (i in 1..10) {
        s += i
    }
    println("1..10=$s")
    for (i in 0 until 3) {
        print("$i ")
    }
    println("")
}
