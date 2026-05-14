class MathUtil {
    static func max(_ a: Int, _ b: Int) -> Int {
        if a > b {
            return a
        }
        return b
    }
}
print(MathUtil.max(3, 7))
print(MathUtil.max(10, 4))
