class Warehouse(val warehouseName: String) {
    val shelves = mutableListOf<Shelf>()
    val orders = mutableListOf<WarehouseOrder>()
    var nextOrderId = 1

    fun addShelf(shelf: Shelf) {
        shelves.add(shelf)
    }

    fun storeItem(item: WarehouseItem): Boolean {
        for (shelf in shelves) {
            if (shelf.addItem(item)) {
                println("  Stored ${item.name} on shelf ${shelf.shelfId}")
                return true
            }
        }
        println("  No space for ${item.name}!")
        return false
    }

    fun findItem(sku: String): WarehouseItem? {
        for (shelf in shelves) {
            val item = shelf.findItem(sku)
            if (item != null) return item
        }
        return null
    }

    fun createOrder(customerName: String): WarehouseOrder {
        val order = WarehouseOrder(nextOrderId, customerName)
        orders.add(order)
        nextOrderId++
        return order
    }

    fun fulfillOrder(order: WarehouseOrder): Boolean {
        println("Fulfilling ${order.describe()}")
        for (line in order.lines) {
            val item = findItem(line.sku)
            if (item == null) {
                println("  Item ${line.sku} not found")
                return false
            }
        }
        for (line in order.lines) {
            for (shelf in shelves) {
                val item = shelf.findItem(line.sku)
                if (item != null) {
                    if (item.quantity < line.quantity) {
                        println("  Insufficient stock for ${item.name}: need ${line.quantity}, have ${item.quantity}")
                        return false
                    }
                    item.quantity -= line.quantity
                    println("  Picked ${line.quantity}x ${item.name} (remaining: ${item.quantity})")
                    break
                }
            }
        }
        order.fulfilled = true
        println("  Order #${order.orderId} fulfilled!")
        return true
    }

    fun totalValue(): Int {
        var sum = 0
        for (shelf in shelves) {
            sum += shelf.shelfValue()
        }
        return sum
    }

    fun printStatus() {
        println("=== Warehouse '$warehouseName' ===")
        for (shelf in shelves) {
            shelf.printShelf()
        }
        println("Total value: ${totalValue()}")
        println("Orders: ${orders.size}")
        for (o in orders) {
            println("  ${o.describe()}")
        }
    }
}
