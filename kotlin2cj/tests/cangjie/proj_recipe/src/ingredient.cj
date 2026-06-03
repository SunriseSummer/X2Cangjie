package proj_recipe

import std.collection.*

class Ingredient <: ToString {
    let name: String
    let amount: Int64
    let unit: String
    init(name: String, amount: Int64, unit: String) {
        this.name = name
        this.amount = amount
        this.unit = unit
    }
    func describe(): String {
        return "${amount} ${unit} ${name}"
    }
    func scale(factor: Int64): Ingredient {
        return Ingredient(name, amount * factor, unit)
    }
    public func toString(): String {
        return "Ingredient(name=${this.name}, amount=${this.amount}, unit=${this.unit})"
    }
}
