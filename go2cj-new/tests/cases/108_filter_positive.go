package main

import "fmt"

func filterPositive(xs []int) []int {
	out := []int{}
	for _, v := range xs {
		if v > 0 {
			out = append(out, v)
		}
	}
	return out
}

func main() {
	xs := []int{-3, 1, -2, 4, 0, 5, -1}
	out := filterPositive(xs)
	for _, v := range out {
		fmt.Println(v)
	}
}
