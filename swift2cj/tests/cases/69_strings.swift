// String operations
let s = "hello world"
print(s.count)
print(s.uppercased())
print(s.lowercased())

// concat + interpolation
let a = "foo"
let b = "bar"
let c = a + b
print(c)
print("\(a)-\(b)")

// build string by appending
var buf = ""
for i in 1 ... 5 {
    buf = buf + "[\(i)]"
}
print(buf)
