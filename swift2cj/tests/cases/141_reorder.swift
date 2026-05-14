// Medium #1 (iter11): reorder recommendation from stock and sales velocity
class StockItem {
    let sku: String
    var stock: Int
    let dailySales: Int
    init(_ sku: String, _ stock: Int, _ dailySales: Int) {
        self.sku = sku
        self.stock = stock
        self.dailySales = dailySales
    }
    func daysLeft() -> Int {
        if dailySales == 0 { return 999 }
        return stock / dailySales
    }
}

func reorderList(_ items: [StockItem], _ threshold: Int) -> [String] {
    var out: [String] = []
    for item in items {
        if item.daysLeft() <= threshold { out.append(item.sku + ":" + "\(item.daysLeft())") }
    }
    return out
}

let items = [
    StockItem("tea", 30, 6),
    StockItem("coffee", 80, 7),
    StockItem("sugar", 12, 0),
    StockItem("milk", 9, 4),
    StockItem("cups", 100, 25)
]
for x in reorderList(items, 5) { print(x) }
