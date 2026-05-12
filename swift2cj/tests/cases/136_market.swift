// Medium #2 (iter10): order book with buy/sell matching
enum Side {
    case buy
    case sell
}

class Order {
    let id: String
    let side: Side
    var qty: Int
    let price: Int
    init(_ id: String, _ side: Side, _ qty: Int, _ price: Int) {
        self.id = id
        self.side = side
        self.qty = qty
        self.price = price
    }
}

class Book {
    var buys: [Order] = []
    var sells: [Order] = []
    func add(_ o: Order) {
        if o.side == .buy { buys.append(o) } else { sells.append(o) }
    }
    func matchOnce() -> String {
        if buys.count == 0 || sells.count == 0 { return "none" }
        var bi = 0
        var si = 0
        var i = 1
        while i < buys.count {
            if buys[i].price > buys[bi].price { bi = i }
            i += 1
        }
        i = 1
        while i < sells.count {
            if sells[i].price < sells[si].price { si = i }
            i += 1
        }
        let b = buys[bi]
        let s = sells[si]
        if b.price < s.price { return "none" }
        var q = b.qty
        if s.qty < q { q = s.qty }
        b.qty -= q
        s.qty -= q
        let line = "trade " + b.id + "/" + s.id + " qty=\(q) price=\(s.price)"
        if b.qty == 0 { buys.remove(at: bi) }
        if s.qty == 0 { sells.remove(at: si) }
        return line
    }
}

let book = Book()
book.add(Order("b1", .buy, 10, 101))
book.add(Order("s1", .sell, 4, 99))
book.add(Order("s2", .sell, 8, 102))
book.add(Order("b2", .buy, 3, 105))
for _ in [0, 1, 2, 3] { print(book.matchOnce()) }
