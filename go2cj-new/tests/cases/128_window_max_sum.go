package main

import "fmt"

func maxWindowSum(xs []int, k int) int {
if k <= 0 || len(xs) < k {
return 0
}
s := 0
for i := 0; i < k; i++ {
s = s + xs[i]
}
best := s
for i := k; i < len(xs); i++ {
s = s + xs[i] - xs[i-k]
if s > best {
best = s
}
}
return best
}

func main() {
fmt.Println(maxWindowSum([]int{1, 3, -2, 5, 3, -1}, 3))
fmt.Println(maxWindowSum([]int{1, 3, -2, 5, 3, -1}, 2))
fmt.Println(maxWindowSum([]int{5}, 2))
}
