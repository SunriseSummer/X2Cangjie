package proj_warehouse

import std.collection.*

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
