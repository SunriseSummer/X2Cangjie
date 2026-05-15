package main

import "fmt"

func sum(xs []int) int {
s := 0
for _, v := range xs {
s += v
}
return s
}

func main() {
xs := []int{1, 2, 3, 4, 5}
fmt.Println(sum(xs))
}
