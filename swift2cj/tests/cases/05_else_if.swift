func grade(_ s: Int) -> String {
    if s >= 90 {
        return "A"
    } else if s >= 80 {
        return "B"
    } else if s >= 70 {
        return "C"
    } else {
        return "F"
    }
}
print(grade(92))
print(grade(81))
print(grade(75))
print(grade(40))
