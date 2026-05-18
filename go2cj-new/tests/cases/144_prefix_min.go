package main

import "fmt"

func prefixMin(a []int) []int {
n := len(a)
out := make([]int, n)
cur := a[0]
for i := 0; i < n; i++ {
if a[i] < cur {
cur = a[i]
}
out[i] = cur
}
return out
}

func main() {
x := prefixMin([]int{5, 3, 4, 2, 8, 1, 6})
fmt.Println(x[0], x[1], x[2], x[3], x[4], x[5], x[6])
y := prefixMin([]int{9, 9, 9, 9})
fmt.Println(y[0], y[1], y[2], y[3])
}
