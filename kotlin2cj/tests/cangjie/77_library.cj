import std.collection.*
import std.deriving.*
import std.sort.*

@Derive[Equatable]
enum Genre <: ToString {
    | FICTION | SCIENCE | HISTORY | ART
    public func toString(): String {
    return match (this) {
                case FICTION => "FICTION"
            case SCIENCE => "SCIENCE"
            case HISTORY => "HISTORY"
            case ART => "ART"
}
    }
}

class Book <: ToString {
    let title: String
    let genre: Genre
    let pages: Int64
    let rating: Int64
    init(title: String, genre: Genre, pages: Int64, rating: Int64) {
        this.title = title
        this.genre = genre
        this.pages = pages
        this.rating = rating
    }
    public func toString(): String {
        return "Book(title=${this.title}, genre=${this.genre}, pages=${this.pages}, rating=${this.rating})"
    }
}

class Library {
    let name: String
    init(name: String) {
        this.name = name
    }
    let books = ArrayList<Book>()
    func add(b: Book) {
        books.add(b)
    }
    func count(): Int64 {
        return books.size
    }
    func totalPages(): Int64 {
        return books.iterator().map({ it => it.pages }).fold<Int64>(0, {acc, x => acc + x})
    }
    func byGenre(g: Genre): ArrayList<Book> {
        return collectArrayList(books.iterator().filter({ it => it.genre == g }))
    }
    func topRated(): Book {
        var best = books[0]
        for (b in books) {
            if (b.rating > best.rating) {
                best = b
            }
        }
        return best
    }
    func averageRating(): Int64 {
        if (books.isEmpty()) {
            return 0
        }
        return books.iterator().map({ it => it.rating }).fold<Int64>(0, {acc, x => acc + x}) / books.size
    }
}

func genreName(g: Genre): String {
    return match (g) {
        case Genre.FICTION => "Fiction"
        case Genre.SCIENCE => "Science"
        case Genre.HISTORY => "History"
        case Genre.ART => "Art"}
}

main() {
    let lib = Library("City")
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
    let top = lib.topRated()
    println("Top: ${top.title} (${top.rating})")
    let sci = lib.byGenre(Genre.SCIENCE)
    print("Science: ")
    for (b in sci) {
        print("${b.title} ")
    }
    println()
    let titles = ({ => let _s = collectArrayList(collectArrayList(lib.books.iterator().map({ it => it.title })).iterator()); sort(_s, stable: true); _s })()
    println("Sorted titles: ${String.join(collectArray<String>(titles.iterator().map({e => e.toString()})), delimiter: ", ")}")
    let highRated = collectArrayList(lib.books.iterator().filter({ it => it.rating >= 9 }))
    println("High rated: ${highRated.size}")
    let genres = ArrayList([Genre.FICTION, Genre.SCIENCE, Genre.HISTORY, Genre.ART])
    for (g in genres) {
        let n = lib.byGenre(g).size
        println("${genreName(g)}: ${n}")
    }
    let byPages = ({ => let _s = collectArrayList(lib.books.iterator()); sort(_s, key: { it => it.pages }, stable: true, descending: true); _s })()
    print("Longest first: ")
    for (b in byPages) {
        print("${b.pages} ")
    }
    println()
    let allGood = lib.books.iterator().all({ it => it.rating >= 5 })
    let anyShort = lib.books.iterator().any({ it => it.pages < 250 })
    println("allGood=${allGood} anyShort=${anyShort}")
}
