protocol Greeter {
    func hello() -> String
}
class Eng: Greeter {
    func hello() -> String {
        return "hi"
    }
}
class Fr: Greeter {
    func hello() -> String {
        return "bonjour"
    }
}
let xs: [Greeter] = [Eng(), Fr()]
for g in xs {
    print(g.hello())
}
