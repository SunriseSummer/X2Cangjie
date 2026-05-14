// Small #2 (iter7): Luhn-style checksum over digit arrays
func checksum(_ digits: [Int]) -> Int {
    var sum = 0
    var doubleIt = false
    var i = digits.count - 1
    while i >= 0 {
        var d = digits[i]
        if doubleIt {
            d *= 2
            if d > 9 {
                d -= 9
            }
        }
        sum += d
        doubleIt = !doubleIt
        i -= 1
    }
    return sum % 10
}

func valid(_ digits: [Int]) -> Bool {
    return checksum(digits) == 0
}

let samples = [
    [4, 9, 9, 2, 7, 3, 9, 8, 7, 1, 6],
    [4, 9, 9, 2, 7, 3, 9, 8, 7, 1, 7],
    [1, 2, 3, 4, 5, 6, 7, 0],
    [7, 9, 9, 2, 7, 3, 9, 8, 7, 1, 3]
]
for s in samples {
    print("\(s) checksum=\(checksum(s)) valid=\(valid(s))")
}
