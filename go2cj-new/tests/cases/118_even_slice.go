package main

import "fmt"

func evenSlice(n int) []int {
	out := make([]int, n)
	for i := 0; i < n; i++ {
		out[i] = 2 * i
	}
	return out
}

func main() {
	xs := evenSlice(6)
	for _, v := range xs {
		fmt.Println(v)
	}
}
