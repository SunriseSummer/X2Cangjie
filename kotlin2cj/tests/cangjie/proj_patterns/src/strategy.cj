package proj_patterns

import std.collection.*
import std.deriving.*

interface Strategy {
    func execute(a: Int64, b: Int64): Int64
    func name(): String
}

class AddStrategy <: Strategy {
    public override func execute(a: Int64, b: Int64): Int64 {
        return a + b
    }
    public override func name(): String {
        return "Add"
    }
}

class SubtractStrategy <: Strategy {
    public override func execute(a: Int64, b: Int64): Int64 {
        return a - b
    }
    public override func name(): String {
        return "Subtract"
    }
}

class MultiplyStrategy <: Strategy {
    public override func execute(a: Int64, b: Int64): Int64 {
        return a * b
    }
    public override func name(): String {
        return "Multiply"
    }
}

class Calculator {
    var strategy: Strategy = AddStrategy()
    func setStrategy(s: Strategy) {
        strategy = s
    }
    func calculate(a: Int64, b: Int64): Int64 {
        return strategy.execute(a, b)
    }
    func currentStrategy(): String {
        return strategy.name()
    }
}
