package main

import "fmt"

func isSorted(xs []int) bool {
for i := 1; i < len(xs); i++ {
if xs[i] < xs[i-1] {
return false
}
}
return true
}

func main() {
fmt.Println(isSorted([]int{1, 2, 2, 3}))
fmt.Println(isSorted([]int{3, 1, 2}))
fmt.Println(isSorted([]int{}))
}
