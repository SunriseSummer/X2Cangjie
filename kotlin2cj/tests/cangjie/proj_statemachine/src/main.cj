package proj_statemachine

import std.collection.*
import std.deriving.*

@Derive[Equatable]

@Derive[Equatable]

main() {
    let sm = StateMachine()
    println(sm.status())
    sm.transition(Event.START)
    println(sm.status())
    sm.transition(Event.PAUSE)
    println(sm.status())
    sm.transition(Event.RESUME)
    println(sm.status())
    sm.transition(Event.STOP)
    println(sm.status())
    sm.transition(Event.START)
    println(sm.status())
    sm.transition(Event.RESET)
    println(sm.status())
    sm.transition(Event.START)
    println(sm.status())
    println("\nTransition log:")
    sm.printLog()
}
