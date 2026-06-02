package proj_library

import std.collection.*

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
