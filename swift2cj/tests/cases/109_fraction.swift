// Small #1 (iter6): rational arithmetic with normalization
struct Fraction {
    var num: Int
    var den: Int

    init(_ n: Int, _ d: Int) {
        var a = n
        var b = d
        if b < 0 {
            a = -a
            b = -b
        }
        let g = gcd(absInt(a), absInt(b))
        self.num = a / g
        self.den = b / g
    }

    func add(_ other: Fraction) -> Fraction {
        return Fraction(num * other.den + other.num * den, den * other.den)
    }

    func mul(_ other: Fraction) -> Fraction {
        return Fraction(num * other.num, den * other.den)
    }

    func neg() -> Fraction {
        return Fraction(-num, den)
    }

    func show() -> String {
        if den == 1 {
            return "\(num)"
        }
        return "\(num)/\(den)"
    }
}

func absInt(_ x: Int) -> Int {
    if x < 0 {
        return -x
    }
    return x
}

func gcd(_ a: Int, _ b: Int) -> Int {
    var x = a
    var y = b
    while y != 0 {
        let r = x % y
        x = y
        y = r
    }
    if x == 0 {
        return 1
    }
    return x
}

let a = Fraction(2, 4)
let b = Fraction(-3, 9)
let c = Fraction(5, -10)
print("a = \(a.show())")
print("b = \(b.show())")
print("c = \(c.show())")
print("a+b = \(a.add(b).show())")
print("a*c = \(a.mul(c).show())")
print("-b = \(b.neg().show())")
