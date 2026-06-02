package proj_inventory

import std.collection.*
import std.deriving.*

enum Category <: ToString {
    | FOOD | ELECTRONICS | CLOTHING | BOOKS
    public func toString(): String {
    return match (this) {
                case FOOD => "FOOD"
            case ELECTRONICS => "ELECTRONICS"
            case CLOTHING => "CLOTHING"
            case BOOKS => "BOOKS"
}
    }
}

class Product <: ToString {
    let name: String
    let price: Float64
    let category: Category
    let quantity: Int64
    init(name: String, price: Float64, category: Category, quantity: Int64) {
        this.name = name
        this.price = price
        this.category = category
        this.quantity = quantity
    }
    public func toString(): String {
        return "Product(name=${this.name}, price=${this.price}, category=${this.category}, quantity=${this.quantity})"
    }
}
