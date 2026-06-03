package proj_warehouse

import std.collection.*

class OrderLine <: ToString {
    let sku: String
    let quantity: Int64
    init(sku: String, quantity: Int64) {
        this.sku = sku
        this.quantity = quantity
    }
    public func toString(): String {
        return "OrderLine(sku=${this.sku}, quantity=${this.quantity})"
    }
}

class WarehouseOrder {
    let orderId: Int64
    let customerName: String
    init(orderId: Int64, customerName: String) {
        this.orderId = orderId
        this.customerName = customerName
    }
    let lines = ArrayList<OrderLine>()
    var fulfilled: Bool = false
    func addLine(sku: String, quantity: Int64) {
        lines.add(OrderLine(sku, quantity))
    }
    func describe(): String {
        let status = if (fulfilled) {
            "fulfilled"
        } else {
            "pending"
        }
        return "Order #${orderId} (${customerName}): ${lines.size} lines [${status}]"
    }
}
