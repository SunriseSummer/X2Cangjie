package proj_warehouse

import std.collection.*

class WarehouseItem <: ToString {
    let sku: String
    let name: String
    var quantity: Int64
    let unitPrice: Int64
    init(sku: String, name: String, quantity: Int64, unitPrice: Int64) {
        this.sku = sku
        this.name = name
        this.quantity = quantity
        this.unitPrice = unitPrice
    }
    func totalValue(): Int64 {
        return quantity * unitPrice
    }
    func describe(): String {
        return "${sku}: ${name} (qty=${quantity}, unit=${unitPrice}, total=${totalValue()})"
    }
    public func toString(): String {
        return "WarehouseItem(sku=${this.sku}, name=${this.name}, quantity=${this.quantity}, unitPrice=${this.unitPrice})"
    }
}
