enum Shape {
    case circle
    case square
    case triangle
}
func name(_ s: Shape) -> String {
    switch s {
    case .circle:
        return "C"
    case .square:
        return "S"
    default:
        return "?"
    }
}
print(name(.circle))
print(name(.square))
print(name(.triangle))
