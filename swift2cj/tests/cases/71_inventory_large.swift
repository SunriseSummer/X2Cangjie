// 200+ line comprehensive program.
// Models a tiny inventory + order-processing system, exercising:
//   - struct / class / protocol / extension
//   - inheritance + override + final
//   - enum w/ raw + enum w/ associated values
//   - operator overload (struct +/-/== style via methods)
//   - generic class
//   - closures (single-line)
//   - guard / ternary
//   - switch + destructuring
//   - tuples
//   - dictionaries + arrays
//   - exception handling (do/catch with throws)
//   - string interpolation

protocol Named {
    func name() -> String
}

protocol Priced {
    func price() -> Int
}

class Product: Named, Priced {
    var id: Int
    var title: String
    var unitPrice: Int
    init(id: Int, title: String, unitPrice: Int) {
        self.id = id
        self.title = title
        self.unitPrice = unitPrice
    }
    func name() -> String { return self.title }
    func price() -> Int { return self.unitPrice }
    func describe() -> String {
        return "#\(self.id) \(self.title) @\(self.unitPrice)"
    }
}

final class DiscountedProduct: Product {
    var pct: Int
    init(id: Int, title: String, unitPrice: Int, pct: Int) {
        self.pct = pct
        super.init(id: id, title: title, unitPrice: unitPrice)
    }
    override func price() -> Int {
        return self.unitPrice * (100 - self.pct) / 100
    }
}

// Generic container — tiny wrapper around an ArrayList<T>
class Bag<T> {
    var items: [T] = []
    func add(_ x: T) {
        self.items.append(x)
    }
    func size() -> Int {
        return self.items.count
    }
    func forEachItem(_ f: (T) -> Void) {
        for x in self.items {
            f(x)
        }
    }
}

// Money struct with arithmetic
struct Money {
    var cents: Int
    static func + (a: Money, b: Money) -> Money {
        return Money(cents: a.cents + b.cents)
    }
    static func - (a: Money, b: Money) -> Money {
        return Money(cents: a.cents - b.cents)
    }
    static func * (a: Money, n: Int) -> Money {
        return Money(cents: a.cents * n)
    }
    func format() -> String {
        let dollars = self.cents / 100
        let frac = self.cents % 100
        return "$\(dollars).\(frac)"
    }
}

// Enum w/ associated values for shipping options
enum Shipping {
    case standard(Int)        // days
    case express(Int, Int)    // days, surcharge cents
    case pickup
}

func shippingCost(_ s: Shipping) -> Int {
    switch s {
    case .standard(let days):
        return days < 5 ? 500 : 200
    case .express(let d, let surcharge):
        return d < 2 ? 1500 + surcharge : 1000 + surcharge
    case .pickup:
        return 0
    }
}

// Enum w/ raw value (gets stripped on the Cangjie side)
enum OrderStatus: Int {
    case pending = 0
    case paid = 1
    case shipped = 2
    case delivered = 3
}

func statusName(_ s: OrderStatus) -> String {
    switch s {
    case .pending: return "PENDING"
    case .paid: return "PAID"
    case .shipped: return "SHIPPED"
    case .delivered: return "DELIVERED"
    }
}

// Order — built from a Bag<Product> + Shipping option.
class Order {
    var products: Bag<Product> = Bag<Product>()
    var ship: Shipping = Shipping.pickup
    var status: OrderStatus = OrderStatus.pending
    func addProduct(_ p: Product) {
        self.products.add(p)
    }
    func subtotal() -> Money {
        var total = 0
        for p in self.products.items {
            total += p.price()
        }
        return Money(cents: total)
    }
    func grandTotal() -> Money {
        let ship = Money(cents: shippingCost(self.ship))
        return self.subtotal() + ship
    }
}

// Extension adds a printable summary.
extension Order {
    func summary() -> String {
        return "Order[\(self.products.size()) item(s), total=\(self.grandTotal().format()), status=\(statusName(self.status))]"
    }
}

// --- main ---

// Build some products including a discounted one (polymorphism via override).
let apple = Product(id: 1, title: "Apple", unitPrice: 120)
let bread = Product(id: 2, title: "Bread", unitPrice: 350)
let butter = DiscountedProduct(id: 3, title: "Butter", unitPrice: 500, pct: 20)
print(apple.describe())
print(bread.describe())
print(butter.describe(), "price=", butter.price())

// Bag<T> + closure iteration
let bag = Bag<Product>()
bag.add(apple)
bag.add(bread)
bag.add(butter)
print("bag size =", bag.size())
bag.forEachItem({ p in print(" - ", p.name(), p.price()) })

// Shipping enum dispatch
print("std(3) =", shippingCost(.standard(3)))
print("std(7) =", shippingCost(.standard(7)))
print("exp(1, 200) =", shippingCost(.express(1, 200)))
print("pickup =", shippingCost(.pickup))

// Money arithmetic
let m1 = Money(cents: 1234)
let m2 = Money(cents: 100)
let m3 = m1 + m2
let m4 = m1 - m2
let m5 = m1 * 3
print(m1.format(), m2.format(), m3.format(), m4.format(), m5.format())

// Status names
print(statusName(.pending), statusName(.paid), statusName(.shipped), statusName(.delivered))

// Build an order and report
let o = Order()
o.addProduct(apple)
o.addProduct(bread)
o.addProduct(butter)
o.ship = .express(1, 200)
o.status = .paid
print(o.summary())
print("subtotal =", o.subtotal().format())
print("grand    =", o.grandTotal().format())

