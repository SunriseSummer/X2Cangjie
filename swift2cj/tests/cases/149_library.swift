// Medium #2 (iter12): library checkout audit with optional dictionary reads
class Book {
    let id: String
    let title: String
    var borrower: String = ""
    init(_ id: String, _ title: String) {
        self.id = id
        self.title = title
    }
    func isBorrowed() -> Bool { return borrower.count > 0 }
}

class Library {
    var books: [String: Book] = [:]
    func add(_ book: Book) { books[book.id] = book }
    func borrow(_ id: String, _ user: String) -> String {
        let b = books[id]
        if let book = b {
            if book.isBorrowed() { return "busy:" + id }
            book.borrower = user
            return "ok:" + id + ":" + user
        }
        return "missing:" + id
    }
    func summary(_ ids: [String]) {
        for id in ids {
            let b = books[id]
            if let book = b {
                print(id + ":" + book.title + ":" + (book.isBorrowed() ? book.borrower : "free"))
            } else {
                print(id + ":missing")
            }
        }
    }
}

let lib = Library()
lib.add(Book("b1", "Algorithms"))
lib.add(Book("b2", "Compilers"))
print(lib.borrow("b1", "alice"))
print(lib.borrow("b1", "bob"))
print(lib.borrow("b3", "carol"))
lib.summary(["b1", "b2", "b3"])
