class Order(val orderId: Int, val customer: Customer, val items: MutableList<CartItem>, val total: Int) {
    var status: String = "pending"

    fun confirm() {
        status = "confirmed"
        val points = total / 10
        customer.earnPoints(points)
        println("Order #$orderId confirmed for ${customer.name}, earned $points points")
    }

    fun describe() {
        println("Order #$orderId [${status}] - ${customer.name} - ${items.size} items - total: $total")
    }
}

class OrderProcessor {
    val orders = mutableListOf<Order>()
    var nextOrderId = 1

    fun checkout(cart: ShoppingCart): Order {
        val order = Order(nextOrderId, cart.customer, cart.items, cart.total())
        orders.add(order)
        nextOrderId++
        return order
    }

    fun processAll() {
        for (order in orders) {
            order.confirm()
        }
    }

    fun printSummary() {
        println("--- Order Summary ---")
        for (order in orders) {
            order.describe()
        }
        println("Total orders: ${orders.size}")
    }
}
