data class OrderLine(val sku: String, val quantity: Int)

class WarehouseOrder(val orderId: Int, val customerName: String) {
    val lines = mutableListOf<OrderLine>()
    var fulfilled: Boolean = false

    fun addLine(sku: String, quantity: Int) {
        lines.add(OrderLine(sku, quantity))
    }

    fun describe(): String {
        val status = if (fulfilled) "fulfilled" else "pending"
        return "Order #$orderId ($customerName): ${lines.size} lines [$status]"
    }
}
