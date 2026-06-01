enum class Light {
    RED, GREEN, YELLOW
}
fun next(l: Light): Light {
    return when (l) {
        Light.RED -> Light.GREEN
        Light.GREEN -> Light.YELLOW
        else -> Light.RED
    }
}
fun label(l: Light): String {
    return when (l) {
        Light.RED -> "stop"
        Light.GREEN -> "go"
        else -> "slow"
    }
}
fun main() {
    var l = Light.RED
    var steps = 0
    while (steps < 6) {
        println(label(l))
        l = next(l)
        steps += 1
    }
}
