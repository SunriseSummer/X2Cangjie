package proj_ecommerce

import std.collection.*

class Order {
    let orderId: Int64
    let customer: Customer
    let items: ArrayList<CartItem>
    let total: Int64
    init(orderId: Int64, customer: Customer, items: ArrayList<CartItem>, total: Int64) {
        this.orderId = orderId
        this.customer = customer
        this.items = items
        this.total = total
    }
    var status: String = "pending"
    func confirm() {
        status = "confirmed"
        let points = total / 10
        customer.earnPoints(points)
        println("Order #${orderId} confirmed for ${customer.name}, earned ${points} points")
    }
    func describe() {
        println("Order #${orderId} [${status}] - ${customer.name} - ${items.size} items - total: ${total}")
    }
}

class OrderProcessor {
    let orders = ArrayList<Order>()
    var nextOrderId = 1
    func checkout(cart: ShoppingCart): Order {
        let order = Order(nextOrderId, cart.customer, cart.items, cart.total())
        orders.add(order)
        nextOrderId += 1
        return order
    }
    func processAll() {
        for (order in orders) {
            order.confirm()
        }
    }
    func printSummary() {
        println("--- Order Summary ---")
        for (order in orders) {
            order.describe()
        }
        println("Total orders: ${orders.size}")
    }
}
