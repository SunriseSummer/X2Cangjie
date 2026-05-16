package main

import "fmt"

func histogram(xs []int, buckets int) []int {
	h := make([]int, buckets)
	for _, v := range xs {
		b := v % buckets
		if b < 0 {
			b = b + buckets
		}
		h[b] = h[b] + 1
	}
	return h
}

func main() {
	xs := []int{0, 1, 2, 3, 4, 0, 1, 2, 0, 1, 0}
	h := histogram(xs, 5)
	for _, v := range h {
		fmt.Println(v)
	}
}
