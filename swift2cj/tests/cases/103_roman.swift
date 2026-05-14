// Small #1 (iter5): Roman numeral encode/decode (no character APIs).
func toRoman(_ n: Int) -> String {
    let vals = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    let syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    var x = n
    var out = ""
    var i = 0
    while i < vals.count {
        while x >= vals[i] {
            out = out + syms[i]
            x -= vals[i]
        }
        i += 1
    }
    return out
}

// Decode by repeated subtractive-pair / single-digit prefix matching.
// Uses only String concatenation and equality on small substrings.
func fromRoman(_ s: String) -> Int {
    let pairs = ["CM", "CD", "XC", "XL", "IX", "IV"]
    let pairV = [900, 400, 90, 40, 9, 4]
    let singles = ["M", "D", "C", "L", "X", "V", "I"]
    let singleV = [1000, 500, 100, 50, 10, 5, 1]
    // Recompute the encoding-from-value as an inverse via toRoman's
    // greedy structure (no per-character API).
    var total = 0
    var cur = ""
    var i = 0
    while i < 4000 {
        let candidate = toRoman(total + 1)
        if candidate.count > s.count {
            return total
        }
        // Try increments by all values; pick the largest that still keeps
        // toRoman(total + v) a prefix-compatible expansion of *s*.
        var picked = 0
        var k = 0
        while k < pairs.count {
            let nv = total + pairV[k]
            if toRoman(nv) == cur + pairs[k] {
                picked = pairV[k]
                cur = cur + pairs[k]
                break
            }
            k += 1
        }
        if picked == 0 {
            k = 0
            while k < singles.count {
                let nv = total + singleV[k]
                if toRoman(nv) == cur + singles[k] {
                    picked = singleV[k]
                    cur = cur + singles[k]
                    break
                }
                k += 1
            }
        }
        if picked == 0 {
            return total
        }
        total += picked
        if cur == s {
            return total
        }
        i += 1
    }
    return total
}

for v in [1, 4, 9, 14, 49, 99, 444, 999, 1994, 3888] {
    let r = toRoman(v)
    let back = fromRoman(r)
    print("\(v) -> \(r) -> \(back)")
}



