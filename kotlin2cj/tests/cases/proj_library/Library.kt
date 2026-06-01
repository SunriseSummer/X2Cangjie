class Library(val libraryName: String) {
    val books = mutableListOf<Book>()
    val members = mutableListOf<Member>()
    val transactions = mutableListOf<Transaction>()
    var nextMemberId = 1

    fun addBook(book: Book) {
        books.add(book)
    }

    fun registerMember(name: String): Member {
        val m = Member(nextMemberId, name)
        members.add(m)
        nextMemberId++
        return m
    }

    fun findBook(isbn: String): Book? {
        for (b in books) {
            if (b.isbn == isbn) return b
        }
        return null
    }

    fun findMember(id: Int): Member? {
        for (m in members) {
            if (m.memberId == id) return m
        }
        return null
    }

    fun checkout(memberId: Int, isbn: String): Boolean {
        val member = findMember(memberId) ?: return false
        val book = findBook(isbn) ?: return false
        val ok = member.borrowBook(book)
        if (ok) {
            transactions.add(Transaction(memberId, isbn, "CHECKOUT"))
            println("  ${member.name} checked out '${book.title}'")
        }
        return ok
    }

    fun doReturn(memberId: Int, isbn: String): Boolean {
        val member = findMember(memberId) ?: return false
        val book = findBook(isbn) ?: return false
        val ok = member.giveBack(book)
        if (ok) {
            transactions.add(Transaction(memberId, isbn, "RETURN"))
            println("  ${member.name} returned '${book.title}'")
        }
        return ok
    }

    fun availableBooks(): Int {
        var count = 0
        for (b in books) {
            if (b.available) count++
        }
        return count
    }

    fun printCatalog() {
        println("=== $libraryName Catalog ===")
        for (b in books) {
            println("  ${b.info()}")
        }
        println("Available: ${availableBooks()}/${books.size}")
    }

    fun printTransactions() {
        println("=== Transaction Log ===")
        for (t in transactions) {
            println("  ${t.describe()}")
        }
    }
}
