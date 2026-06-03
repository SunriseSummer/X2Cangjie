package proj_patterns

import std.collection.*
import std.deriving.*

enum TrafficLight <: ToString {
    | RED | YELLOW | GREEN
    public func toString(): String {
    return match (this) {
                case RED => "RED"
            case YELLOW => "YELLOW"
            case GREEN => "GREEN"
}
    }
}

func nextLight(light: TrafficLight): TrafficLight {
    return match (light) {
        case TrafficLight.RED => TrafficLight.GREEN
        case TrafficLight.GREEN => TrafficLight.YELLOW
        case TrafficLight.YELLOW => TrafficLight.RED}
}

func lightAction(light: TrafficLight): String {
    return match (light) {
        case TrafficLight.RED => "Stop"
        case TrafficLight.YELLOW => "Caution"
        case TrafficLight.GREEN => "Go"}
}

class TrafficController {
    var state: TrafficLight = TrafficLight.RED
    let log = ArrayList<String>()
    func currentState(): String {
        return state.toString()
    }
    func currentAction(): String {
        return lightAction(state)
    }
    func advance(): String {
        let oldState = state
        state = nextLight(state)
        let msg = "${oldState} -> ${state} (${lightAction(state)})"
        log.add(msg)
        return msg
    }
}
