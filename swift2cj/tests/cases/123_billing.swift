// Medium #1 (iter8): invoice billing with taxes and discounts
class LineItem {
    let sku: String
    let qty: Int
    let unit: Int
    init(_ sku: String, _ qty: Int, _ unit: Int) {
        self.sku = sku
        self.qty = qty
        self.unit = unit
    }
    func subtotal() -> Int {
        return qty * unit
    }
}

class Invoice {
    let id: String
    var items: [LineItem] = []
    var discount: Int = 0
    init(_ id: String) {
        self.id = id
    }
    func add(_ item: LineItem) {
        items.append(item)
    }
    func totalBeforeDiscount() -> Int {
        var s = 0
        for item in items { s += item.subtotal() }
        return s
    }
    func total() -> Int {
        let raw = totalBeforeDiscount()
        let afterDiscount = raw - discount
        if afterDiscount < 0 { return 0 }
        return afterDiscount + (afterDiscount * 8) / 100
    }
    func summary() -> String {
        return id + ": raw=\(totalBeforeDiscount()) discount=\(discount) total=\(total())"
    }
}

let a = Invoice("A100")
a.add(LineItem("pen", 10, 3))
a.add(LineItem("book", 2, 25))
a.discount = 5
let b = Invoice("B200")
b.add(LineItem("bag", 1, 80))
b.add(LineItem("pencil", 5, 2))
b.discount = 0
for inv in [a, b] {
    print(inv.summary())
}
