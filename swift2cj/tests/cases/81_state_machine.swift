// Medium #1 (iter2): state machine for a traffic light (~80 lines)
enum Light {
    case red
    case yellow
    case green
}

class TrafficLight {
    var state: Light = .red
    var ticks: Int = 0
    var history: [String] = []

    func step() {
        ticks += 1
        switch state {
        case .red:
            state = .green
        case .green:
            state = .yellow
        case .yellow:
            state = .red
        }
        history.append(name())
    }

    func name() -> String {
        switch state {
        case .red:
            return "RED"
        case .yellow:
            return "YELLOW"
        case .green:
            return "GREEN"
        }
    }

    func reset() {
        state = .red
        ticks = 0
        history = []
    }
}

let t = TrafficLight()
print("start = \(t.name())")
var i = 0
while i < 7 {
    t.step()
    print("tick \(t.ticks): \(t.name())")
    i += 1
}
print("history size = \(t.history.count)")

t.reset()
print("after reset = \(t.name()) ticks=\(t.ticks) history=\(t.history.count)")

// Multi-light scenario
let lights: [TrafficLight] = [TrafficLight(), TrafficLight(), TrafficLight()]
// stagger them
lights[1].step()
lights[2].step()
lights[2].step()
var idx = 0
for l in lights {
    print("L\(idx) = \(l.name())")
    idx += 1
}

// run 3 more ticks on each
for l in lights {
    l.step()
    l.step()
    l.step()
}
idx = 0
for l in lights {
    print("L\(idx) after 3 ticks = \(l.name()) (total \(l.ticks))")
    idx += 1
}
