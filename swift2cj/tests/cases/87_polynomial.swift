// Medium #1 (iter3): polynomial with addition / multiplication / evaluation (~100 lines)
class Poly {
    var coeffs: [Int] = []  // coeffs[i] is coefficient of x^i

    init(_ cs: [Int]) {
        coeffs = cs
    }

    func degree() -> Int {
        return coeffs.count - 1
    }

    func eval(_ x: Int) -> Int {
        var r = 0
        var pw = 1
        for c in coeffs {
            r += c * pw
            pw *= x
        }
        return r
    }

    func add(_ other: Poly) -> Poly {
        let a = coeffs
        let b = other.coeffs
        let na = a.count
        let nb = b.count
        let n: Int
        if na >= nb {
            n = na
        } else {
            n = nb
        }
        var out: [Int] = []
        var i = 0
        while i < n {
            var s = 0
            if i < na {
                s += a[i]
            }
            if i < nb {
                s += b[i]
            }
            out.append(s)
            i += 1
        }
        return Poly(out)
    }

    func mul(_ other: Poly) -> Poly {
        let a = coeffs
        let b = other.coeffs
        let na = a.count
        let nb = b.count
        let n = na + nb - 1
        var out: [Int] = []
        var k = 0
        while k < n {
            out.append(0)
            k += 1
        }
        var i = 0
        while i < na {
            var j = 0
            while j < nb {
                out[i + j] += a[i] * b[j]
                j += 1
            }
            i += 1
        }
        return Poly(out)
    }

    func show() -> String {
        var s = ""
        var i = 0
        var first = true
        for c in coeffs {
            if c != 0 {
                if !first {
                    s = s + " + "
                }
                s = s + "\(c)x^\(i)"
                first = false
            }
            i += 1
        }
        if first {
            s = "0"
        }
        return s
    }
}

let p1 = Poly([1, 2, 3])      // 1 + 2x + 3x^2
let p2 = Poly([4, 0, 5])      // 4 + 5x^2
print("p1 = \(p1.show())  deg=\(p1.degree())")
print("p2 = \(p2.show())  deg=\(p2.degree())")
print("p1(2) = \(p1.eval(2))")
print("p2(3) = \(p2.eval(3))")

let pAdd = p1.add(p2)
print("p1+p2 = \(pAdd.show())  deg=\(pAdd.degree())")

let pMul = p1.mul(p2)
print("p1*p2 = \(pMul.show())  deg=\(pMul.degree())")
print("(p1*p2)(1) = \(pMul.eval(1))")
print("(p1*p2)(2) = \(pMul.eval(2))")
