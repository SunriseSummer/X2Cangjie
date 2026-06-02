package proj_patterns

import std.collection.*
import std.deriving.*

interface Coffee {
    func cost(): Int64
    func description(): String
}

class SimpleCoffee <: Coffee {
    public override func cost(): Int64 {
        return 5
    }
    public override func description(): String {
        return "Simple coffee"
    }
}

class MilkDecorator <: Coffee {
    let inner: Coffee
    init(inner: Coffee) {
        this.inner = inner
    }
    public override func cost(): Int64 {
        return inner.cost() + 2
    }
    public override func description(): String {
        return inner.description().toString() + " + milk"
    }
}

class SugarDecorator <: Coffee {
    let inner: Coffee
    init(inner: Coffee) {
        this.inner = inner
    }
    public override func cost(): Int64 {
        return inner.cost() + 1
    }
    public override func description(): String {
        return inner.description().toString() + " + sugar"
    }
}

class WhipDecorator <: Coffee {
    let inner: Coffee
    init(inner: Coffee) {
        this.inner = inner
    }
    public override func cost(): Int64 {
        return inner.cost() + 3
    }
    public override func description(): String {
        return inner.description().toString() + " + whip"
    }
}

func buildCoffee(addMilk: Bool, addSugar: Bool, addWhip: Bool): Coffee {
    var coffee: Coffee = SimpleCoffee()
    if (addMilk) {
        coffee = MilkDecorator(coffee)
    }
    if (addSugar) {
        coffee = SugarDecorator(coffee)
    }
    if (addWhip) {
        coffee = WhipDecorator(coffee)
    }
    return coffee
}
