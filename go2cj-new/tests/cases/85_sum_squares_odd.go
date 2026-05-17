package main

import "fmt"

func sumSquaresOddIndex(xs []int) int {
	s := 0
	for i, v := range xs {
		if i%2 == 1 {
			s = s + v*v
		}
	}
	return s
}

func main() {
	xs := []int{1, 2, 3, 4, 5}
	fmt.Println(sumSquaresOddIndex(xs))
	ys := []int{10, 20, 30, 40}
	fmt.Println(sumSquaresOddIndex(ys))
}
