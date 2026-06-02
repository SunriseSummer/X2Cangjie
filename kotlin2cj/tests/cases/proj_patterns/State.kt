enum class TrafficLight {
    RED,
    YELLOW,
    GREEN
}

fun nextLight(light: TrafficLight): TrafficLight {
    return when (light) {
        TrafficLight.RED -> TrafficLight.GREEN
        TrafficLight.GREEN -> TrafficLight.YELLOW
        TrafficLight.YELLOW -> TrafficLight.RED
    }
}

fun lightAction(light: TrafficLight): String {
    return when (light) {
        TrafficLight.RED -> "Stop"
        TrafficLight.YELLOW -> "Caution"
        TrafficLight.GREEN -> "Go"
    }
}

class TrafficController {
    private var state: TrafficLight = TrafficLight.RED
    val log = ArrayList<String>()

    fun currentState(): String = state.toString()
    fun currentAction(): String = lightAction(state)

    fun advance(): String {
        val oldState = state
        state = nextLight(state)
        val msg = "$oldState -> $state (${lightAction(state)})"
        log.add(msg)
        return msg
    }
}
