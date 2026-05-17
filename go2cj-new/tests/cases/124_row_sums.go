package main

import "fmt"

func rowSums(mat [][]int) []int {
out := make([]int, len(mat))
for i := 0; i < len(mat); i++ {
s := 0
for _, v := range mat[i] {
s = s + v
}
out[i] = s
}
return out
}

func main() {
mat := [][]int{{1, 2, 3}, {4, 5}, {6}}
rs := rowSums(mat)
for _, v := range rs {
fmt.Println(v)
}
}
