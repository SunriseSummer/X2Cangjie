// Ranges & loops
var sum = 0
for i in 1 ... 10 {
    sum += i
}
print(sum)

var prod = 1
for i in 1 ..< 6 {
    prod *= i
}
print(prod)

// while
var n = 1
var count = 0
while n < 100 {
    n *= 2
    count += 1
}
print(n, count)

// reversed range via stride-like: count down using while
var k = 5
while k > 0 {
    print(k)
    k -= 1
}
