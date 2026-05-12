// Small #2 (iter3): hand-rolled higher-order helpers over int arrays
func mapInt(_ xs: [Int], _ f: (Int) -> Int) -> [Int] {
    var out: [Int] = []
    for x in xs {
        out.append(f(x))
    }
    return out
}

func filterInt(_ xs: [Int], _ p: (Int) -> Bool) -> [Int] {
    var out: [Int] = []
    for x in xs {
        if p(x) {
            out.append(x)
        }
    }
    return out
}

func reduceInt(_ xs: [Int], _ initial: Int, _ f: (Int, Int) -> Int) -> Int {
    var acc = initial
    for x in xs {
        acc = f(acc, x)
    }
    return acc
}

let xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
let sq = mapInt(xs, { x in x * x })
print("squares: \(sq)")

let even = filterInt(xs, { x in x % 2 == 0 })
print("evens: \(even)")

let sum = reduceInt(xs, 0, { (a, b) in a + b })
let prod = reduceInt(xs, 1, { (a, b) in a * b })
print("sum=\(sum) prod=\(prod)")

let evenSq = mapInt(filterInt(xs, { x in x % 2 == 0 }), { x in x * x })
print("even squares: \(evenSq)")
