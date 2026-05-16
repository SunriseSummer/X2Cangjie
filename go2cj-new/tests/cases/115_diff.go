package main

import "fmt"

func diff(xs []int) []int {
	n := len(xs)
	if n < 2 {
		return []int{}
	}
	out := make([]int, n-1)
	for i := 1; i < n; i++ {
		out[i-1] = xs[i] - xs[i-1]
	}
	return out
}

func main() {
	xs := []int{1, 3, 6, 10, 15}
	d := diff(xs)
	for _, v := range d {
		fmt.Println(v)
	}
}
