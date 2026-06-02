class Shelf(val shelfId: String, val capacity: Int) {
    val items = mutableListOf<WarehouseItem>()

    fun addItem(item: WarehouseItem): Boolean {
        if (items.size >= capacity) return false
        items.add(item)
        return true
    }

    fun findItem(sku: String): WarehouseItem? {
        for (item in items) {
            if (item.sku == sku) return item
        }
        return null
    }

    fun removeItem(sku: String): WarehouseItem? {
        for (i in 0 until items.size) {
            if (items[i].sku == sku) {
                return items.removeAt(i)
            }
        }
        return null
    }

    fun usedSlots(): Int = items.size
    fun freeSlots(): Int = capacity - items.size

    fun shelfValue(): Int {
        var sum = 0
        for (item in items) {
            sum += item.totalValue()
        }
        return sum
    }

    fun printShelf() {
        println("Shelf $shelfId (${usedSlots()}/$capacity):")
        for (item in items) {
            println("  ${item.describe()}")
        }
    }
}
