// Large #2 (iter3): shopping cart with discount strategies (~250 lines)
class Product {
    let sku: String
    let name: String
    let price: Int  // cents
    let category: String
    init(sku: String, name: String, price: Int, category: String) {
        self.sku = sku
        self.name = name
        self.price = price
        self.category = category
    }
}

class LineItem {
    let product: Product
    var qty: Int
    init(product: Product, qty: Int) {
        self.product = product
        self.qty = qty
    }
    func subtotal() -> Int {
        return product.price * qty
    }
}

// Strategy base class
class Discount {
    func apply(_ items: [LineItem]) -> Int {
        return 0
    }
    func name() -> String {
        return "none"
    }
}

class PercentOff: Discount {
    let pct: Int
    let category: String
    init(pct: Int, category: String) {
        self.pct = pct
        self.category = category
    }
    override func apply(_ items: [LineItem]) -> Int {
        var total = 0
        for it in items {
            if it.product.category == category {
                total += it.subtotal()
            }
        }
        return (total * pct) / 100
    }
    override func name() -> String {
        return "\(pct)% off \(category)"
    }
}

class FlatOff: Discount {
    let amount: Int
    let threshold: Int
    init(amount: Int, threshold: Int) {
        self.amount = amount
        self.threshold = threshold
    }
    override func apply(_ items: [LineItem]) -> Int {
        var total = 0
        for it in items {
            total += it.subtotal()
        }
        if total >= threshold {
            return amount
        }
        return 0
    }
    override func name() -> String {
        return "flat -\(amount) over \(threshold)"
    }
}

class BulkOff: Discount {
    let sku: String
    let minQty: Int
    let perUnitOff: Int
    init(sku: String, minQty: Int, perUnitOff: Int) {
        self.sku = sku
        self.minQty = minQty
        self.perUnitOff = perUnitOff
    }
    override func apply(_ items: [LineItem]) -> Int {
        for it in items {
            if it.product.sku == sku && it.qty >= minQty {
                return it.qty * perUnitOff
            }
        }
        return 0
    }
    override func name() -> String {
        return "bulk \(sku)≥\(minQty) -\(perUnitOff)/each"
    }
}

class Cart {
    var items: [LineItem] = []
    var discounts: [Discount] = []

    func add(_ p: Product, qty: Int) {
        items.append(LineItem(product: p, qty: qty))
    }

    func addDiscount(_ d: Discount) {
        discounts.append(d)
    }

    func gross() -> Int {
        var g = 0
        for it in items {
            g += it.subtotal()
        }
        return g
    }

    func discountTotal() -> Int {
        var d = 0
        for disc in discounts {
            d += disc.apply(items)
        }
        return d
    }

    func net() -> Int {
        return gross() - discountTotal()
    }

    func report() {
        for it in items {
            print("  \(it.product.sku) x\(it.qty) = \(it.subtotal())")
        }
        for d in discounts {
            print("  -- \(d.name()) -\(d.apply(items))")
        }
        print("  gross=\(gross()) discount=\(discountTotal()) net=\(net())")
    }
}

let apple = Product(sku: "A1", name: "Apple", price: 100, category: "fruit")
let banana = Product(sku: "B1", name: "Banana", price: 50, category: "fruit")
let bread = Product(sku: "X9", name: "Bread", price: 250, category: "bakery")
let milk = Product(sku: "M1", name: "Milk", price: 300, category: "dairy")

let c1 = Cart()
c1.add(apple, qty: 5)
c1.add(banana, qty: 4)
c1.add(bread, qty: 1)
c1.addDiscount(PercentOff(pct: 10, category: "fruit"))
print("cart1:")
c1.report()

let c2 = Cart()
c2.add(milk, qty: 2)
c2.add(bread, qty: 2)
c2.addDiscount(FlatOff(amount: 100, threshold: 1000))
c2.addDiscount(FlatOff(amount: 50, threshold: 500))
print("cart2:")
c2.report()

let c3 = Cart()
c3.add(apple, qty: 12)
c3.add(banana, qty: 2)
c3.addDiscount(BulkOff(sku: "A1", minQty: 10, perUnitOff: 8))
c3.addDiscount(PercentOff(pct: 5, category: "fruit"))
print("cart3:")
c3.report()

// Empty discount stack
let c4 = Cart()
c4.add(bread, qty: 3)
print("cart4 (no discount): net=\(c4.net())")
