// State machine pattern: traffic light simulation
enum class LightColor {
    RED, YELLOW, GREEN
}

class TrafficLight(var color: LightColor) {
    var ticks = 0

    fun tick() {
        ticks++
        color = when (color) {
            LightColor.RED -> if (ticks >= 3) { ticks = 0; LightColor.GREEN } else color
            LightColor.GREEN -> if (ticks >= 4) { ticks = 0; LightColor.YELLOW } else color
            LightColor.YELLOW -> if (ticks >= 1) { ticks = 0; LightColor.RED } else color
        }
    }

    fun display(): String = when (color) {
        LightColor.RED -> "[R]"
        LightColor.GREEN -> "[G]"
        LightColor.YELLOW -> "[Y]"
    }
}

fun main() {
    val light = TrafficLight(LightColor.RED)
    val history = ArrayList<String>()

    for (i in 0 until 16) {
        history.add(light.display())
        light.tick()
    }
    println("Traffic: ${history.joinToString(" ")}")

    // Count each color
    var r = 0
    var g = 0
    var y = 0
    for (h in history) {
        when (h) {
            "[R]" -> r++
            "[G]" -> g++
            "[Y]" -> y++
        }
    }
    println("Red: $r, Green: $g, Yellow: $y")
    println("Total: ${history.size}")
}
