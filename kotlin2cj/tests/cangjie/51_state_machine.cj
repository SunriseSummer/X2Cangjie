import std.deriving.*

@Derive[Equatable]
enum Light <: ToString {
    | RED | GREEN | YELLOW
    public func toString(): String {
    return match (this) {
                case RED => "RED"
            case GREEN => "GREEN"
            case YELLOW => "YELLOW"
}
    }
}

func next(l: Light): Light {
    return match (l) {
        case Light.RED => Light.GREEN
        case Light.GREEN => Light.YELLOW
        case _ => Light.RED}
}

func label(l: Light): String {
    return match (l) {
        case Light.RED => "stop"
        case Light.GREEN => "go"
        case _ => "slow"}
}

main() {
    var l = Light.RED
    var steps = 0
    while (steps < 6) {
        println(label(l))
        l = next(l)
        steps += 1
    }
}
