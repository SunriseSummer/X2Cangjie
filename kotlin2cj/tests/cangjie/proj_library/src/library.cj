package proj_library

import std.collection.*

class Library {
    let libraryName: String
    init(libraryName: String) {
        this.libraryName = libraryName
    }
    let books = ArrayList<Book>()
    let members = ArrayList<Member>()
    let transactions = ArrayList<Transaction>()
    var nextMemberId = 1
    func addBook(book: Book) {
        books.add(book)
    }
    func registerMember(name: String): Member {
        let m = Member(nextMemberId, name)
        members.add(m)
        nextMemberId += 1
        return m
    }
    func findBook(isbn: String): ?Book {
        for (b in books) {
            if (b.isbn == isbn) {
                return b
            }
        }
        return None
    }
    func findMember(id: Int64): ?Member {
        for (m in members) {
            if (m.memberId == id) {
                return m
            }
        }
        return None
    }
    func checkout(memberId: Int64, isbn: String): Bool {
        let member = findMember(memberId) ?? return
        false
        let book = findBook(isbn) ?? return
        false
        let ok = member.borrowBook(book)
        if (ok) {
            transactions.add(Transaction(memberId, isbn, "CHECKOUT"))
            println("  ${member.name} checked out '${book.title}'")
        }
        return ok
    }
    func doReturn(memberId: Int64, isbn: String): Bool {
        let member = findMember(memberId) ?? return
        false
        let book = findBook(isbn) ?? return
        false
        let ok = member.giveBack(book)
        if (ok) {
            transactions.add(Transaction(memberId, isbn, "RETURN"))
            println("  ${member.name} returned '${book.title}'")
        }
        return ok
    }
    func availableBooks(): Int64 {
        var count = 0
        for (b in books) {
            if (b.available) {
                count += 1
            }
        }
        return count
    }
    func printCatalog() {
        println("=== ${libraryName} Catalog ===")
        for (b in books) {
            println("  ${b.info()}")
        }
        println("Available: ${availableBooks()}/${books.size}")
    }
    func printTransactions() {
        println("=== Transaction Log ===")
        for (t in transactions) {
            println("  ${t.describe()}")
        }
    }
}
