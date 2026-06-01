import std.collection.*
import std.deriving.*

@Derive[Equatable]
enum Category <: ToString {
    | FOOD | BOOK | TOY | TOOL
    public func toString(): String {
    return match (this) {
                case FOOD => "FOOD"
            case BOOK => "BOOK"
            case TOY => "TOY"
            case TOOL => "TOOL"
}
    }
}

class Item <: ToString {
    let name: String
    let category: Category
    let price: Int64
    let qty: Int64
    init(name: String, category: Category, price: Int64, qty: Int64) {
        this.name = name
        this.category = category
        this.price = price
        this.qty = qty
    }
    public func toString(): String {
        return "Item(name=${this.name}, category=${this.category}, price=${this.price}, qty=${this.qty})"
    }
}

class Store {
    let name: String
    init(name: String) {
        this.name = name
    }
    let items = ArrayList<Item>()
    func add(item: Item) {
        items.add(item)
    }
    func totalValue(): Int64 {
        var sum = 0
        for (it in items) {
            sum += it.price * it.qty
        }
        return sum
    }
    func countIn(cat: Category): Int64 {
        return collectArrayList(items.iterator().filter({ it => it.category == cat })).size
    }
    func mostExpensive(): Item {
        var best = items[0]
        for (it in items) {
            if (it.price > best.price) {
                best = it
            }
        }
        return best
    }
}

func label(cat: Category): String {
    return match (cat) {
        case Category.FOOD => "Food"
        case Category.BOOK => "Book"
        case Category.TOY => "Toy"
        case Category.TOOL => "Tool"}
}

main() {
    let store = Store("Corner")
    store.add(Item("Bread", Category.FOOD, 3, 20))
    store.add(Item("Novel", Category.BOOK, 12, 5))
    store.add(Item("Block", Category.TOY, 8, 10))
    store.add(Item("Hammer", Category.TOOL, 15, 4))
    store.add(Item("Apple", Category.FOOD, 1, 50))
    println("Store: ${store.name}")
    println("Items: ${store.items.size}")
    println("Total value: ${store.totalValue()}")
    println("Food items: ${store.countIn(Category.FOOD)}")
    let top = store.mostExpensive()
    println("Top: ${top.name} (${label(top.category)}) @ ${top.price}")
    let prices = collectArrayList(store.items.iterator().map({ it => it.price }))
    println("Max price: ${prices.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0}")
    println("Sum price: ${prices.iterator().fold<Int64>(0, {acc, x => acc + x})}")
    let cheap = collectArrayList(store.items.iterator().filter({ it => it.price < 10 }))
    print("Cheap: ")
    for (c in cheap) {
        print("${c.name} ")
    }
    println()
    var grand = 0
    for (cat in ArrayList([Category.FOOD, Category.BOOK, Category.TOY, Category.TOOL])) {
        let n = store.countIn(cat)
        println("${label(cat)}: ${n} kind(s)")
        grand += n
    }
    println("Distinct entries: ${grand}")
}
