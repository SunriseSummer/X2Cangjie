package main

import "fmt"

func reverse(xs []int) []int {
	n := len(xs)
	out := make([]int, n)
	for i := 0; i < n; i++ {
		out[n-1-i] = xs[i]
	}
	return out
}

func main() {
	r := reverse([]int{1, 2, 3, 4, 5})
	for _, v := range r {
		fmt.Println(v)
	}
}
