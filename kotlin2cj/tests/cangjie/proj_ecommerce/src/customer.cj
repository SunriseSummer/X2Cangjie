package proj_ecommerce

import std.collection.*

class Customer {
    let name: String
    let id: Int64
    init(name: String, id: Int64) {
        this.name = name
        this.id = id
    }
    var loyaltyPoints: Int64 = 0
    func earnPoints(amount: Int64) {
        loyaltyPoints += amount
    }
    func info(): String {
        return "Customer(${name}, id=${id}, points=${loyaltyPoints})"
    }
}
