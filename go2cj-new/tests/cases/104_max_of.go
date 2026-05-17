package main

import "fmt"

func maxOf(xs []int) int {
	m := xs[0]
	for _, v := range xs {
		if v > m {
			m = v
		}
	}
	return m
}

func main() {
	xs := []int{4, 2, 9, 1, 7}
	fmt.Println(maxOf(xs))
	ys := []int{-1, -5, -2}
	fmt.Println(maxOf(ys))
}
