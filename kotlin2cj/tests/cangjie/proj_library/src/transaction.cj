package proj_library

import std.collection.*

class Transaction <: ToString {
    let memberId: Int64
    let bookIsbn: String
    let action: String
    init(memberId: Int64, bookIsbn: String, action: String) {
        this.memberId = memberId
        this.bookIsbn = bookIsbn
        this.action = action
    }
    func describe(): String {
        return "${action}: member=${memberId}, book=${bookIsbn}"
    }
    public func toString(): String {
        return "Transaction(memberId=${this.memberId}, bookIsbn=${this.bookIsbn}, action=${this.action})"
    }
}
