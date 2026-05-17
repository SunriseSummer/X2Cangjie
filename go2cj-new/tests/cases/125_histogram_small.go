package main

import "fmt"

func histogram(xs []int, k int) []int {
h := make([]int, k)
for _, v := range xs {
if v >= 0 && v < k {
h[v] = h[v] + 1
}
}
return h
}

func main() {
h := histogram([]int{1, 3, 1, 2, 3, 3, 0}, 5)
for _, v := range h {
fmt.Println(v)
}
}
