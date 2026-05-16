package main

import "fmt"

func main() {
	xs := []int{1, 2, 3, 4, 5}
	r := make([]int, 0, len(xs))
	for i := len(xs) - 1; i >= 0; i-- {
		r = append(r, xs[i])
	}
	for _, v := range r {
		fmt.Println(v)
	}
}
