package main

import "fmt"

func matvec(m [][]int, v []int) []int {
out := make([]int, len(m))
for i := 0; i < len(m); i++ {
s := 0
for j := 0; j < len(v); j++ {
s = s + m[i][j]*v[j]
}
out[i] = s
}
return out
}

func main() {
m := [][]int{{1, 2, 0, -1}, {0, 3, 5, 2}, {4, 0, 1, 1}}
v := []int{2, 1, 3, 4}
out := matvec(m, v)
for _, x := range out {
fmt.Println(x)
}
}
