enum class Genre { FICTION, SCIENCE, HISTORY, ART }

data class Book(val title: String, val genre: Genre, val pages: Int, val rating: Int)

class Library(val name: String) {
    val books = ArrayList<Book>()

    fun add(b: Book) {
        books.add(b)
    }

    fun count(): Int = books.count()

    fun totalPages(): Int = books.sumOf { it.pages }

    fun byGenre(g: Genre): List<Book> = books.filter { it.genre == g }

    fun topRated(): Book {
        var best = books[0]
        for (b in books) {
            if (b.rating > best.rating) best = b
        }
        return best
    }

    fun averageRating(): Int {
        if (books.isEmpty()) return 0
        return books.sumOf { it.rating } / books.count()
    }
}

fun genreName(g: Genre): String = when (g) {
    Genre.FICTION -> "Fiction"
    Genre.SCIENCE -> "Science"
    Genre.HISTORY -> "History"
    Genre.ART -> "Art"
}

fun main() {
    val lib = Library("City")
    lib.add(Book("Dune", Genre.SCIENCE, 412, 9))
    lib.add(Book("Sapiens", Genre.HISTORY, 443, 8))
    lib.add(Book("1984", Genre.FICTION, 328, 10))
    lib.add(Book("Cosmos", Genre.SCIENCE, 365, 9))
    lib.add(Book("Art Book", Genre.ART, 200, 6))
    lib.add(Book("Hobbit", Genre.FICTION, 310, 8))

    println("Library: ${lib.name}")
    println("Books: ${lib.count()}")
    println("Total pages: ${lib.totalPages()}")
    println("Avg rating: ${lib.averageRating()}")

    val top = lib.topRated()
    println("Top: ${top.title} (${top.rating})")

    val sci = lib.byGenre(Genre.SCIENCE)
    print("Science: ")
    for (b in sci) print("${b.title} ")
    println()

    val titles = lib.books.map { it.title }.sorted()
    println("Sorted titles: ${titles.joinToString(", ")}")

    val highRated = lib.books.filter { it.rating >= 9 }
    println("High rated: ${highRated.count()}")

    val genres = listOf(Genre.FICTION, Genre.SCIENCE, Genre.HISTORY, Genre.ART)
    for (g in genres) {
        val n = lib.byGenre(g).count()
        println("${genreName(g)}: $n")
    }

    val byPages = lib.books.sortedByDescending { it.pages }
    print("Longest first: ")
    for (b in byPages) print("${b.pages} ")
    println()

    val allGood = lib.books.all { it.rating >= 5 }
    val anyShort = lib.books.any { it.pages < 250 }
    println("allGood=$allGood anyShort=$anyShort")
}
