package main

import "fmt"

func prefixSums(xs []int) []int {
out := make([]int, len(xs))
s := 0
for i, v := range xs {
s = s + v
out[i] = s
}
return out
}

func main() {
xs := []int{3, 1, 4, 1, 5}
ps := prefixSums(xs)
for _, v := range ps {
fmt.Println(v)
}
}
