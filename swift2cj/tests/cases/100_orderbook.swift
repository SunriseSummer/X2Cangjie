// Medium #2 (iter5): order-book matching simulator (~150 lines)
class Order {
    let id: Int
    let isBuy: Bool
    let price: Int
    var qty: Int

    init(id: Int, isBuy: Bool, price: Int, qty: Int) {
        self.id = id
        self.isBuy = isBuy
        self.price = price
        self.qty = qty
    }
}

class Trade {
    let buyer: Int
    let seller: Int
    let price: Int
    let qty: Int
    init(buyer: Int, seller: Int, price: Int, qty: Int) {
        self.buyer = buyer
        self.seller = seller
        self.price = price
        self.qty = qty
    }
    func show() -> String {
        return "BUY#\(buyer) <-> SELL#\(seller) qty=\(qty) @\(price)"
    }
}

class Book {
    var bids: [Order] = []   // descending price
    var asks: [Order] = []   // ascending price
    var trades: [Trade] = []

    func insertSorted(_ o: Order, _ list: inout [Order], _ desc: Bool) {
        var i = 0
        while i < list.count {
            if desc {
                if o.price > list[i].price {
                    break
                }
            } else {
                if o.price < list[i].price {
                    break
                }
            }
            i += 1
        }
        list.insert(o, at: i)
    }

    func place(_ o: Order) {
        if o.isBuy {
            match(o, &asks, true)
            if o.qty > 0 {
                insertSorted(o, &bids, true)
            }
        } else {
            match(o, &bids, false)
            if o.qty > 0 {
                insertSorted(o, &asks, false)
            }
        }
    }

    func match(_ o: Order, _ book: inout [Order], _ isBidLooking: Bool) {
        while o.qty > 0 && book.count > 0 {
            let top = book[0]
            // Buy: take ask if ask.price <= buy.price
            // Sell: take bid if bid.price >= sell.price
            let cross: Bool
            if isBidLooking {
                cross = top.price <= o.price
            } else {
                cross = top.price >= o.price
            }
            if !cross {
                return
            }
            let n: Int
            if o.qty < top.qty {
                n = o.qty
            } else {
                n = top.qty
            }
            let buyerId: Int
            let sellerId: Int
            if o.isBuy {
                buyerId = o.id
                sellerId = top.id
            } else {
                buyerId = top.id
                sellerId = o.id
            }
            trades.append(Trade(buyer: buyerId, seller: sellerId, price: top.price, qty: n))
            o.qty -= n
            top.qty -= n
            if top.qty == 0 {
                book.remove(at: 0)
            }
        }
    }

    func depth() {
        print("BIDS:")
        for b in bids {
            print("  #\(b.id) \(b.qty) @ \(b.price)")
        }
        print("ASKS:")
        for a in asks {
            print("  #\(a.id) \(a.qty) @ \(a.price)")
        }
    }
}

let book = Book()
book.place(Order(id: 1, isBuy: true,  price: 100, qty: 5))
book.place(Order(id: 2, isBuy: true,  price: 102, qty: 3))
book.place(Order(id: 3, isBuy: false, price: 105, qty: 4))
book.place(Order(id: 4, isBuy: false, price: 103, qty: 6))
book.place(Order(id: 5, isBuy: true,  price: 104, qty: 7))   // crosses ask@103

print("== trades ==")
for t in book.trades {
    print(t.show())
}
print("trade count = \(book.trades.count)")
print("== depth after ==")
book.depth()

// Big sweep buy
book.place(Order(id: 6, isBuy: true, price: 110, qty: 20))
print("== after sweep buy ==")
for t in book.trades {
    print(t.show())
}
book.depth()
