// Small #1 (iter10): leap year and day-of-year calculations
func isLeap(_ y: Int) -> Bool {
    if y % 400 == 0 { return true }
    if y % 100 == 0 { return false }
    return y % 4 == 0
}

func daysInMonth(_ y: Int, _ m: Int) -> Int {
    let base = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if m == 2 && isLeap(y) { return 29 }
    return base[m - 1]
}

func dayOfYear(_ y: Int, _ m: Int, _ d: Int) -> Int {
    var total = d
    var i = 1
    while i < m {
        total += daysInMonth(y, i)
        i += 1
    }
    return total
}

let samples = [(2024, 2, 29), (2023, 3, 1), (2000, 12, 31), (1900, 3, 1)]
for s in samples {
    print("\(s.0)-\(s.1)-\(s.2) leap=\(isLeap(s.0)) doy=\(dayOfYear(s.0, s.1, s.2))")
}
