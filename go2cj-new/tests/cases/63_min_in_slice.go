package main

import "fmt"

func minOf(xs []int) int {
	m := xs[0]
	for _, v := range xs {
		if v < m {
			m = v
		}
	}
	return m
}

func main() {
	xs := []int{3, 1, 4, 1, 5, 9, 2, 6}
	fmt.Println(minOf(xs))
	ys := []int{-3, -1, -7, -2}
	fmt.Println(minOf(ys))
}
