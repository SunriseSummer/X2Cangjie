enum class State {
    IDLE,
    RUNNING,
    PAUSED,
    STOPPED
}

enum class Event {
    START,
    PAUSE,
    RESUME,
    STOP,
    RESET
}

class StateMachine {
    var currentState: State = State.IDLE
    val log = mutableListOf<String>()

    fun transition(event: Event) {
        val oldState = currentState
        val newState = when (currentState) {
            State.IDLE -> when (event) {
                Event.START -> State.RUNNING
                else -> State.IDLE
            }
            State.RUNNING -> when (event) {
                Event.PAUSE -> State.PAUSED
                Event.STOP -> State.STOPPED
                else -> State.RUNNING
            }
            State.PAUSED -> when (event) {
                Event.RESUME -> State.RUNNING
                Event.STOP -> State.STOPPED
                else -> State.PAUSED
            }
            State.STOPPED -> when (event) {
                Event.RESET -> State.IDLE
                else -> State.STOPPED
            }
        }
        currentState = newState
        log.add("$oldState + $event -> $newState")
    }

    fun printLog() {
        for (entry in log) {
            println("  $entry")
        }
    }

    fun status(): String = "Current: $currentState"
}
