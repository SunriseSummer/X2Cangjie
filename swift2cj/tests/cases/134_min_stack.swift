// Small #2 (iter10): stack with minimum tracking
class MinStack {
    var values: [Int] = []
    var mins: [Int] = []
    func push(_ x: Int) {
        values.append(x)
        if mins.count == 0 || x < mins[mins.count - 1] { mins.append(x) } else { mins.append(mins[mins.count - 1]) }
    }
    func pop() -> Int {
        let v = values[values.count - 1]
        values.remove(at: values.count - 1)
        mins.remove(at: mins.count - 1)
        return v
    }
    func minValue() -> Int { return mins[mins.count - 1] }
    func size() -> Int { return values.count }
}

let st = MinStack()
for v in [5, 3, 7, 2, 2, 9] {
    st.push(v)
    print("push \(v) min=\(st.minValue()) size=\(st.size())")
}
while st.size() > 0 {
    let oldMin = st.minValue()
    let p = st.pop()
    print("pop \(p) oldMin=\(oldMin) size=\(st.size())")
}
