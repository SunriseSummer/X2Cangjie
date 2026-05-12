// operator overload via static func +/-
struct V2 {
    var x: Int
    var y: Int
    static func + (a: V2, b: V2) -> V2 {
        return V2(x: a.x + b.x, y: a.y + b.y)
    }
    static func - (a: V2, b: V2) -> V2 {
        return V2(x: a.x - b.x, y: a.y - b.y)
    }
    static func * (a: V2, k: Int) -> V2 {
        return V2(x: a.x * k, y: a.y * k)
    }
}
let p = V2(x: 1, y: 2)
let q = V2(x: 10, y: 20)
let r = p + q
let d = q - p
let s = p * 5
print(r.x, r.y)
print(d.x, d.y)
print(s.x, s.y)
