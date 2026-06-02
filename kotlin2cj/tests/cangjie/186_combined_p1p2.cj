import std.collection.*

class Logger {
    private init() {}
    public static let INSTANCE = Logger()
    var messages = ArrayList<String>()
    func log(msg: String) {
        messages.add(msg)
    }
    func dump(): String {
        return String.join(collectArray<String>(messages.iterator().map({e => e.toString()})), delimiter: "; ")
    }
}

func sum(nums: Array<Int64>): Int64 {
    var total = 0
    for (n in nums) {
        total += n
    }
    return total
}

main() {
    let greeting = { => "Hello from lazy!" }()
    println(greeting)
    Logger.INSTANCE.log("start")
    Logger.INSTANCE.log("process")
    Logger.INSTANCE.log("end")
    println(Logger.INSTANCE.dump())
    println(sum(1, 2, 3, 4, 5))
    let nums = ArrayList([10, 20, 30])
    let doubled = collectArrayList(nums.iterator().map({ it => it * 2 }))
    println(String.join(collectArray<String>(doubled.iterator().map({e => e.toString()})), delimiter: ", "))
}
