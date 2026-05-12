func kind(_ n: Int) -> String {
    switch n {
    case 1, 3, 5, 7, 9:
        return "odd"
    case 2, 4, 6, 8:
        return "even"
    default:
        return "other"
    }
}
print(kind(3))
print(kind(4))
print(kind(11))
