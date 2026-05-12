// Medium #2 (iter5): tiny run-length encoder / decoder, alphabet-driven.
//
// We work entirely with String prefixes / equality so the translation
// doesn't have to thread per-character Rune semantics.  The encoder splits
// *s* by greedily consuming maximal runs whose first character matches
// the current alphabet probe.

let alpha = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o",
             "p","q","r","s","t","u","v","w","x","y","z","0","1","2","3",
             "4","5","6","7","8","9"]

func leadChar(_ s: String) -> String {
    var i = 0
    while i < alpha.count {
        if s.hasPrefix(alpha[i]) {
            return alpha[i]
        }
        i += 1
    }
    return ""
}

func dropOne(_ s: String) -> String {
    let lead = leadChar(s)
    if lead == "" {
        return s
    }
    // Build the suffix by probing what continues to match after ``lead``.
    var out = ""
    var i = 0
    while i < alpha.count {
        if s.hasPrefix(lead + out + alpha[i]) {
            out = out + alpha[i]
            i = 0
            continue
        }
        i += 1
    }
    return out
}

func encodeRLE(_ s: String) -> String {
    if s.count == 0 {
        return ""
    }
    var rest = s
    var out = ""
    while rest.count > 0 {
        let ch = leadChar(rest)
        if ch == "" {
            break
        }
        var run = 0
        while rest.hasPrefix(ch) {
            rest = dropOne(rest)
            run += 1
        }
        out = out + ch + "\(run)"
    }
    return out
}

func isDigit(_ c: String) -> Bool {
    let digs = ["0","1","2","3","4","5","6","7","8","9"]
    var i = 0
    while i < digs.count {
        if c == digs[i] {
            return true
        }
        i += 1
    }
    return false
}

func digitValue(_ c: String) -> Int {
    let digs = ["0","1","2","3","4","5","6","7","8","9"]
    var i = 0
    while i < digs.count {
        if c == digs[i] {
            return i
        }
        i += 1
    }
    return 0
}

func decodeRLE(_ s: String) -> String {
    var rest = s
    var out = ""
    while rest.count > 0 {
        let ch = leadChar(rest)
        if ch == "" {
            break
        }
        rest = dropOne(rest)
        var num = 0
        while rest.count > 0 {
            let d = leadChar(rest)
            if !isDigit(d) {
                break
            }
            num = num * 10 + digitValue(d)
            rest = dropOne(rest)
        }
        var k = 0
        while k < num {
            out = out + ch
            k += 1
        }
    }
    return out
}

let samples = ["aaabbc", "x", "abc", "aabbbccccd", "wwwwwwwwwwzz", ""]
for s in samples {
    let enc = encodeRLE(s)
    let dec = decodeRLE(enc)
    let ok = (dec == s)
    print("'\(s)' -> '\(enc)' -> '\(dec)' ok=\(ok)")
}

func ratio(_ s: String) -> Double {
    if s.count == 0 {
        return 0.0
    }
    let e = encodeRLE(s)
    return Double(e.count) / Double(s.count)
}
print("ratio aaaaaaaa = \(ratio("aaaaaaaa"))")
print("ratio abcd = \(ratio("abcd"))")


