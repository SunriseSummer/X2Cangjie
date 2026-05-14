// enum with raw value (Int) — raw value is dropped on the Cangjie side
enum Status: Int {
    case ok = 0
    case warn = 1
    case fail = 2
}
func name(_ s: Status) -> String {
    switch s {
    case .ok: return "OK"
    case .warn: return "WARN"
    case .fail: return "FAIL"
    }
}
print(name(.ok))
print(name(.warn))
print(name(.fail))
