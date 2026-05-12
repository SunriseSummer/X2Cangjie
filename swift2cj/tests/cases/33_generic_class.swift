class Box<T> {
    var value: T
    init(_ v: T) {
        self.value = v
    }
    func get() -> T {
        return self.value
    }
}
let b: Box<Int> = Box(42)
print(b.get())
