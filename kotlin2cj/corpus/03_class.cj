class Point {
    let x: Int64
    let y: Int64
    init(x: Int64, y: Int64) {
        this.x = x
        this.y = y
    }
    func sumSquares(): Int64 {
        return (x * x) + (y * y)
    }
}
