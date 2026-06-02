package proj_warehouse

import std.collection.*

class Warehouse {
    let warehouseName: String
    init(warehouseName: String) {
        this.warehouseName = warehouseName
    }
    let shelves = ArrayList<Shelf>()
    let orders = ArrayList<WarehouseOrder>()
    var nextOrderId = 1
    func addShelf(shelf: Shelf) {
        shelves.add(shelf)
    }
    func storeItem(item: WarehouseItem): Bool {
        for (shelf in shelves) {
            if (shelf.addItem(item)) {
                println("  Stored ${item.name} on shelf ${shelf.shelfId}")
                return true
            }
        }
        println("  No space for ${item.name}!")
        return false
    }
    func findItem(sku: String): ?WarehouseItem {
        for (shelf in shelves) {
            let item = shelf.findItem(sku)
            if (let Some(item) <- item) {
                return item
            }
        }
        return None
    }
    func createOrder(customerName: String): WarehouseOrder {
        let order = WarehouseOrder(nextOrderId, customerName)
        orders.add(order)
        nextOrderId += 1
        return order
    }
    func fulfillOrder(order: WarehouseOrder): Bool {
        println("Fulfilling ${order.describe()}")
        for (line in order.lines) {
            let item = findItem(line.sku)
            if (item.isNone()) {
                println("  Item ${line.sku} not found")
                return false
            }
        }
        for (line in order.lines) {
            for (shelf in shelves) {
                let item = shelf.findItem(line.sku)
                if (let Some(item) <- item) {
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
    func totalValue(): Int64 {
        var sum = 0
        for (shelf in shelves) {
            sum += shelf.shelfValue()
        }
        return sum
    }
    func printStatus() {
        println("=== Warehouse '${warehouseName}' ===")
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
