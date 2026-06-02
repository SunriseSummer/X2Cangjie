class Counter {
    private init() {}
    public static let INSTANCE = Counter()
    var count = 0
    func increment() {
        count += 1
    }
    func getCount(): Int64 {
        return count
    }
}

main() {
    Counter.INSTANCE.increment()
    Counter.INSTANCE.increment()
    Counter.INSTANCE.increment()
    println(Counter.INSTANCE.getCount())
    println(Counter.INSTANCE.count)
}
