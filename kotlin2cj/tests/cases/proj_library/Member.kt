class Member(val memberId: Int, val name: String) {
    val borrowedBooks = mutableListOf<Book>()
    val borrowHistory = mutableListOf<String>()

    fun borrowBook(book: Book): Boolean {
        if (!book.available) return false
        if (borrowedBooks.size >= 3) return false
        book.available = false
        borrowedBooks.add(book)
        borrowHistory.add("Borrowed: ${book.title}")
        return true
    }

    fun giveBack(book: Book): Boolean {
        var found = false
        for (i in 0 until borrowedBooks.size) {
            if (borrowedBooks[i].isbn == book.isbn) {
                borrowedBooks.removeAt(i)
                book.available = true
                borrowHistory.add("Returned: ${book.title}")
                found = true
                break
            }
        }
        return found
    }

    fun currentBorrows(): Int = borrowedBooks.size

    fun printHistory() {
        println("History for $name:")
        for (entry in borrowHistory) {
            println("  $entry")
        }
    }
}
