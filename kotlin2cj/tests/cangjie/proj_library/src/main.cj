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

class Member {
    let memberId: Int64
    let name: String
    init(memberId: Int64, name: String) {
        this.memberId = memberId
        this.name = name
    }
    let borrowedBooks = ArrayList<Book>()
    let borrowHistory = ArrayList<String>()
    func borrowBook(book: Book): Bool {
        if (!book.available) {
            return false
        }
        if (borrowedBooks.size >= 3) {
            return false
        }
        book.available = false
        borrowedBooks.add(book)
        borrowHistory.add("Borrowed: ${book.title}")
        return true
    }
    func giveBack(book: Book): Bool {
        var found = false
        for (i in 0..borrowedBooks.size) {
            if (borrowedBooks[i].isbn == book.isbn) {
                borrowedBooks.remove(at: i)
                book.available = true
                borrowHistory.add("Returned: ${book.title}")
                found = true
                break
            }
        }
        return found
    }
    func currentBorrows(): Int64 {
        return borrowedBooks.size
    }
    func printHistory() {
        println("History for ${name}:")
        for (entry in borrowHistory) {
            println("  ${entry}")
        }
    }
}

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

main() {
    let lib = Library("City Library")
    lib.addBook(Book("001", "Design Patterns", "GoF", 1994))
    lib.addBook(Book("002", "Clean Code", "Martin", 2008))
    lib.addBook(Book("003", "Refactoring", "Fowler", 1999))
    lib.addBook(Book("004", "SICP", "Abelson", 1985))
    lib.addBook(Book("005", "TAOCP", "Knuth", 1968))
    let alice = lib.registerMember("Alice")
    let bob = lib.registerMember("Bob")
    println("Initial catalog:")
    lib.printCatalog()
    println("\nCheckouts:")
    lib.checkout(alice.memberId, "001")
    lib.checkout(alice.memberId, "003")
    lib.checkout(bob.memberId, "002")
    lib.checkout(bob.memberId, "001")
    println("\nAfter checkouts:")
    lib.printCatalog()
    println("\nReturns:")
    lib.doReturn(alice.memberId, "001")
    println("\nAfter return:")
    lib.printCatalog()
    println()
    lib.printTransactions()
    println()
    alice.printHistory()
    println()
    bob.printHistory()
    println("\nAlice borrows: ${alice.currentBorrows()}")
    println("Bob borrows: ${bob.currentBorrows()}")
}