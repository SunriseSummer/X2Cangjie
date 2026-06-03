package proj_warehouse

import std.collection.*

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
