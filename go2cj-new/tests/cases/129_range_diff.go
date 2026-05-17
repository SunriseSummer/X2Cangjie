package main

import "fmt"

func rangeDiff(xs []int) int {
if len(xs) == 0 {
return 0
}
mn := xs[0]
mx := xs[0]
for _, v := range xs {
if v < mn {
mn = v
}
if v > mx {
mx = v
}
}
return mx - mn
}

func main() {
fmt.Println(rangeDiff([]int{4, 1, 9, 3}))
fmt.Println(rangeDiff([]int{-5, -2, -10}))
fmt.Println(rangeDiff([]int{7}))
}
