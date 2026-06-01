class Rect(val w: Int, val h: Int) {
    fun area(): Int = w * h
}
class Box(val name: String, val rect: Rect) {
    fun describe(): String {
        return "$name area=${rect.area()}"
    }
}
fun main() {
    val r = Rect(3, 5)
    val b = Box("panel", r)
    println(b.describe())
}
