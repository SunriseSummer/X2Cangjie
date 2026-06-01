import std.collection.*
import std.deriving.*
import std.sort.*

@Derive[Equatable]
enum Category <: ToString {
    | BOOK | FOOD | TOY | TECH
    public func toString(): String {
    return match (this) {
                case BOOK => "BOOK"
            case FOOD => "FOOD"
            case TOY => "TOY"
            case TECH => "TECH"
}
    }
}

class Product <: ToString {
    let id: Int64
    let name: String
    let price: Int64
    let category: Category
    init(id: Int64, name: String, price: Int64, category: Category) {
        this.id = id
        this.name = name
        this.price = price
        this.category = category
    }
    public func toString(): String {
        return "Product(id=${this.id}, name=${this.name}, price=${this.price}, category=${this.category})"
    }
}

class OrderLine <: ToString {
    let product: Product
    let qty: Int64
    init(product: Product, qty: Int64) {
        this.product = product
        this.qty = qty
    }
    public func toString(): String {
        return "OrderLine(product=${this.product}, qty=${this.qty})"
    }
}

class Order {
    let id: Int64
    let customer: String
    init(id: Int64, customer: String) {
        this.id = id
        this.customer = customer
    }
    let lines = ArrayList<OrderLine>()
    func addLine(p: Product, qty: Int64) {
        lines.add(OrderLine(p, qty))
    }
    func subtotal(): Int64 {
        var total = 0
        for (l in lines) {
            total = total + (l.product.price * l.qty)
        }
        return total
    }
    func itemCount(): Int64 {
        var n = 0
        for (l in lines) {
            n = n + l.qty
        }
        return n
    }
    func categories(): ArrayList<Category> {
        let seen = ArrayList<Category>()
        for (l in lines) {
            if (!seen.contains(l.product.category)) {
                seen.add(l.product.category)
            }
        }
        return seen
    }
}

class Catalog {
    let products = ArrayList<Product>()
    var nextId = 1
    func add(name: String, price: Int64, cat: Category): Product {
        let p = Product(nextId, name, price, cat)
        products.add(p)
        nextId = nextId + 1
        return p
    }
    func findByCategory(cat: Category): ArrayList<Product> {
        let out = ArrayList<Product>()
        for (p in products) {
            if (p.category == cat) {
                out.add(p)
            }
        }
        return out
    }
    func cheapest(): Product {
        var best = products[0]
        for (p in products) {
            if (p.price < best.price) {
                best = p
            }
        }
        return best
    }
    func priciest(): Product {
        var best = products[0]
        for (p in products) {
            if (p.price > best.price) {
                best = p
            }
        }
        return best
    }
}

func discountFor(total: Int64): Int64 {
    return if (total >= 1000) {
        total / 10
    } else if (total >= 500) {
        total / 20
    } else if (total >= 100) {
        total / 50
    } else {
        0
    }
}

func categoryLabel(c: Category): String {
    return match (c) {
        case Category.BOOK => "Books"
        case Category.FOOD => "Groceries"
        case Category.TOY => "Toys"
        case Category.TECH => "Electronics"}
}

func formatMoney(cents: Int64): String {
    let dollars = cents / 100
    let rem = cents % 100
    let r = if (rem < 10) {
        "0${rem}"
    } else {
        "${rem}"
    }
    return "\$${dollars}.${r}"
}

class Report {
    let counters = HashMap<String, Int64>()
    func record(key: String, amount: Int64) {
        counters[key] = (counters.get(key) ?? 0) + amount
    }
    func dump() {
        let keys = ArrayList<String>()
        for (k in counters.keys()) {
            keys.add(k)
        }
        sort(keys, stable: true)
        for (k in keys) {
            println("  ${k}: ${counters[k]}")
        }
    }
}

main() {
    let catalog = Catalog()
    catalog.add("Kotlin in Action", 4500, Category.BOOK)
    catalog.add("Apple", 50, Category.FOOD)
    catalog.add("Lego Set", 8000, Category.TOY)
    catalog.add("Headphones", 12000, Category.TECH)
    catalog.add("Cookbook", 3000, Category.BOOK)
    catalog.add("Bread", 250, Category.FOOD)
    catalog.add("Puzzle", 1500, Category.TOY)
    catalog.add("Mouse", 2500, Category.TECH)
    println("=== Catalog ===")
    for (p in catalog.products) {
        println("${p.id}. ${p.name} [${categoryLabel(p.category)}] ${formatMoney(p.price)}")
    }
    println("Cheapest: ${catalog.cheapest().name}")
    println("Priciest: ${catalog.priciest().name}")
    println("=== Books ===")
    let books = catalog.findByCategory(Category.BOOK)
    for (b in books) {
        println("- ${b.name}")
    }
    let orders = ArrayList<Order>()
    let o1 = Order(1, "Alice")
    o1.addLine(catalog.products[0], 1)
    o1.addLine(catalog.products[3], 2)
    orders.add(o1)
    let o2 = Order(2, "Bob")
    o2.addLine(catalog.products[1], 10)
    o2.addLine(catalog.products[5], 3)
    o2.addLine(catalog.products[6], 1)
    orders.add(o2)
    let o3 = Order(3, "Carol")
    o3.addLine(catalog.products[2], 1)
    o3.addLine(catalog.products[7], 2)
    o3.addLine(catalog.products[4], 1)
    orders.add(o3)
    let report = Report()
    var grandTotal = 0
    println("=== Orders ===")
    for (o in orders) {
        let sub = o.subtotal()
        let disc = discountFor(sub)
        let net = sub - disc
        grandTotal = grandTotal + net
        println("Order #${o.id} (${o.customer}): items=${o.itemCount()} sub=${formatMoney(sub)} disc=${formatMoney(disc)} net=${formatMoney(net)}")
        for (c in o.categories()) {
            report.record(categoryLabel(c), 1)
        }
        report.record("revenue", net)
    }
    println("=== Report ===")
    report.dump()
    println("Grand total: ${formatMoney(grandTotal)}")
    let allPrices = ArrayList<Int64>()
    for (p in catalog.products) {
        allPrices.add(p.price)
    }
    let sumPrices = allPrices.iterator().fold<Int64>(0, {acc, x => acc + x})
    let avgPrice = sumPrices / allPrices.size
    println("Avg catalog price: ${formatMoney(avgPrice)}")
    let expensive = collectArrayList(allPrices.iterator().filter({ it => it > 2000 }))
    println("Expensive count: ${expensive.size}")
    let doubled = collectArrayList(allPrices.iterator().map({ it => it * 2 }))
    var dsum = 0
    for (d in doubled) {
        dsum = dsum + d
    }
    println("Doubled sum: ${dsum}")
    let sorted = ({ => let _s = collectArrayList(allPrices.iterator()); sort(_s, stable: true); _s })()
    println("Sorted prices: ${sorted}")
    println("Min: ${sorted[0]} Max: ${sorted[sorted.size - 1]}")
}
