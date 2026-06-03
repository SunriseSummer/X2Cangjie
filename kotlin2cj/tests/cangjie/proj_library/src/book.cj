package proj_library

import std.collection.*

class Book <: ToString {
    let isbn: String
    let title: String
    let author: String
    let year: Int64
    init(isbn: String, title: String, author: String, year: Int64) {
        this.isbn = isbn
        this.title = title
        this.author = author
        this.year = year
    }
    var available: Bool = true
    func info(): String {
        let status = if (available) {
            "available"
        } else {
            "checked out"
        }
        return "${title} by ${author} (${year}) [${status}]"
    }
    public func toString(): String {
        return "Book(isbn=${this.isbn}, title=${this.title}, author=${this.author}, year=${this.year})"
    }
}
