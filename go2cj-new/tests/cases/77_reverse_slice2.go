package main

import "fmt"

func reverseSlice(xs []int) []int {
	n := len(xs)
	out := make([]int, n)
	for i := 0; i < n; i++ {
		out[i] = xs[n-1-i]
	}
	return out
}

func main() {
	xs := []int{1, 2, 3, 4, 5}
	r := reverseSlice(xs)
	for _, v := range r {
		fmt.Println(v)
	}
}
