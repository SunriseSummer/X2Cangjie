package proj_statemachine

import std.collection.*
import std.deriving.*

enum State <: ToString {
    | IDLE | RUNNING | PAUSED | STOPPED
    public func toString(): String {
    return match (this) {
                case IDLE => "IDLE"
            case RUNNING => "RUNNING"
            case PAUSED => "PAUSED"
            case STOPPED => "STOPPED"
}
    }
}

enum Event <: ToString {
    | START | PAUSE | RESUME | STOP | RESET
    public func toString(): String {
    return match (this) {
                case START => "START"
            case PAUSE => "PAUSE"
            case RESUME => "RESUME"
            case STOP => "STOP"
            case RESET => "RESET"
}
    }
}

class StateMachine {
    var currentState: State = State.IDLE
    let log = ArrayList<String>()
    func transition(event: Event) {
        let oldState = currentState
        let newState = match (currentState) {
            case State.IDLE => 
                match (event) {
                    case Event.START => State.RUNNING
                    case _ => State.IDLE}
            case State.RUNNING => 
                match (event) {
                    case Event.PAUSE => State.PAUSED
                    case Event.STOP => State.STOPPED
                    case _ => State.RUNNING}
            case State.PAUSED => 
                match (event) {
                    case Event.RESUME => State.RUNNING
                    case Event.STOP => State.STOPPED
                    case _ => State.PAUSED}
            case State.STOPPED => 
                match (event) {
                    case Event.RESET => State.IDLE
                    case _ => State.STOPPED}}
        currentState = newState
        log.add("${oldState} + ${event} -> ${newState}")
    }
    func printLog() {
        for (entry in log) {
            println("  ${entry}")
        }
    }
    func status(): String {
        return "Current: ${currentState}"
    }
}
