// enum with associated values + match destructure
enum Shape {
    case rect(Int, Int)
    case circle(Int)
    case square(Int)
}
func area(_ s: Shape) -> Int {
    switch s {
    case .rect(let w, let h):
        return w * h
    case .circle(let r):
        return 3 * r * r
    case .square(let a):
        return a * a
    }
}
print(area(.rect(3, 4)))
print(area(.circle(5)))
print(area(.square(6)))
