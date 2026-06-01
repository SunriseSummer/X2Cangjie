import std.collection.*
import std.deriving.*

@Derive[Equatable]
enum LightColor <: ToString {
    | RED | YELLOW | GREEN
    public func toString(): String {
    return match (this) {
                case RED => "RED"
            case YELLOW => "YELLOW"
            case GREEN => "GREEN"
}
    }
}

class TrafficLight {
    var color: LightColor
    init(color: LightColor) {
        this.color = color
    }
    var ticks = 0
    func tick() {
        ticks += 1
        color = match (color) {
            case LightColor.RED => 
                if (ticks >= 3) {
                    ticks = 0
                    LightColor.GREEN
                } else {
                    color
                }
            case LightColor.GREEN => 
                if (ticks >= 4) {
                    ticks = 0
                    LightColor.YELLOW
                } else {
                    color
                }
            case LightColor.YELLOW => 
                if (ticks >= 1) {
                    ticks = 0
                    LightColor.RED
                } else {
                    color
                }}
    }
    func display(): String {
        return match (color) {
            case LightColor.RED => "[R]"
            case LightColor.GREEN => "[G]"
            case LightColor.YELLOW => "[Y]"}
    }
}

main() {
    let light = TrafficLight(LightColor.RED)
    let history = ArrayList<String>()
    for (i in 0..16) {
        history.add(light.display())
        light.tick()
    }
    println("Traffic: ${String.join(collectArray<String>(history.iterator().map({e => e.toString()})), delimiter: " ")}")
    var r = 0
    var g = 0
    var y = 0
    for (h in history) {
        match (h) {
            case "[R]" => r += 1
            case "[G]" => g += 1
            case "[Y]" => y += 1
            case _ => ()}
    }
    println("Red: ${r}, Green: ${g}, Yellow: ${y}")
    println("Total: ${history.size}")
}
