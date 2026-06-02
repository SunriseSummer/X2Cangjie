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

class Shelf {
    let shelfId: String
    let capacity: Int64
    init(shelfId: String, capacity: Int64) {
        this.shelfId = shelfId
        this.capacity = capacity
    }
    let items = ArrayList<WarehouseItem>()
    func addItem(item: WarehouseItem): Bool {
        if (items.size >= capacity) {
            return false
        }
        items.add(item)
        return true
    }
    func findItem(sku: String): ?WarehouseItem {
        for (item in items) {
            if (item.sku == sku) {
                return item
            }
        }
        return None
    }
    func removeItem(sku: String): ?WarehouseItem {
        for (i in 0..items.size) {
            if (items[i].sku == sku) {
                return items.remove(at: i)
            }
        }
        return None
    }
    func usedSlots(): Int64 {
        return items.size
    }
    func freeSlots(): Int64 {
        return capacity - items.size
    }
    func shelfValue(): Int64 {
        var sum = 0
        for (item in items) {
            sum += item.totalValue()
        }
        return sum
    }
    func printShelf() {
        println("Shelf ${shelfId} (${usedSlots()}/${capacity}):")
        for (item in items) {
            println("  ${item.describe()}")
        }
    }
}

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

main() {
    let wh = Warehouse("Central")
    wh.addShelf(Shelf("A1", 3))
    wh.addShelf(Shelf("A2", 3))
    wh.addShelf(Shelf("B1", 2))
    println("Stocking warehouse:")
    wh.storeItem(WarehouseItem("SKU001", "Widget", 100, 5))
    wh.storeItem(WarehouseItem("SKU002", "Gadget", 50, 15))
    wh.storeItem(WarehouseItem("SKU003", "Doohickey", 200, 2))
    wh.storeItem(WarehouseItem("SKU004", "Thingamajig", 30, 25))
    wh.storeItem(WarehouseItem("SKU005", "Whatchamacallit", 80, 8))
    wh.storeItem(WarehouseItem("SKU006", "Gizmo", 60, 12))
    wh.storeItem(WarehouseItem("SKU007", "Sprocket", 40, 10))
    wh.storeItem(WarehouseItem("SKU008", "Doodad", 90, 3))
    wh.storeItem(WarehouseItem("SKU009", "Contraption", 20, 50))
    println()
    wh.printStatus()
    println()
    let order1 = wh.createOrder("Alice")
    order1.addLine("SKU001", 10)
    order1.addLine("SKU003", 50)
    wh.fulfillOrder(order1)
    println()
    let order2 = wh.createOrder("Bob")
    order2.addLine("SKU002", 5)
    order2.addLine("SKU004", 100)
    wh.fulfillOrder(order2)
    println()
    wh.printStatus()
}