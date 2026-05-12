class Animal {
    var name: String
    init(_ name: String) {
        self.name = name
    }
    func speak() -> String {
        return "..."
    }
}
class Dog: Animal {
    override init(_ name: String) {
        super.init(name)
    }
    override func speak() -> String {
        return "woof"
    }
}
let a: Animal = Animal("a")
let d: Animal = Dog("rex")
print(a.speak())
print(d.speak())
