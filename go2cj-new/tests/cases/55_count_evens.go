package main

import "fmt"

func countEvens(xs []int) int {
	c := 0
	for _, v := range xs {
		if v%2 == 0 {
			c = c + 1
		}
	}
	return c
}

func main() {
	xs := []int{1, 2, 3, 4, 5, 6, 7, 8}
	fmt.Println(countEvens(xs))
	ys := []int{10, 20, 31, 40}
	fmt.Println(countEvens(ys))
}
