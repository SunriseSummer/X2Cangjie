import std.collection.*
import std.deriving.*

@Derive[Equatable]
enum Category <: ToString {
    | FOOD | TOOL | BOOK
    public func toString(): String {
    return match (this) {
                case FOOD => "FOOD"
            case TOOL => "TOOL"
            case BOOK => "BOOK"
}
    }
}

class Item {
    let name: String
    let category: Category
    var qty: Int64
    init(name: String, category: Category, qty: Int64) {
        this.name = name
        this.category = category
        this.qty = qty
    }
    func restock(amount: Int64) {
        qty += amount
    }
}

func categoryName(c: Category): String {
    return match (c) {
        case Category.FOOD => "food"
        case Category.TOOL => "tool"
        case _ => "book"}
}

main() {
    let items = ArrayList<Item>()
    items.add(Item("apple", Category.FOOD, 3))
    items.add(Item("hammer", Category.TOOL, 1))
    items.add(Item("novel", Category.BOOK, 5))
    items[0].restock(7)
    var total = 0
    for (it in items) {
        total += it.qty
        println("${it.name} [${categoryName(it.category)}] x${it.qty}")
    }
    println("total=${total}")
    let counts = HashMap<String, Int64>()
    for (it in items) {
        let key = categoryName(it.category)
        counts[key] = (counts.get(key) ?? 0) + it.qty
    }
    var food = counts.get("food") ?? 0
    println("food count=${food}")
}
