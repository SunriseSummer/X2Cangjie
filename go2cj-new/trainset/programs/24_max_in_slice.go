package main

import "fmt"

func main() {
	xs := []int{5, 3, 8, 1, 9, 2}
	maxv := xs[0]
	for _, v := range xs {
		if v > maxv {
			maxv = v
		}
	}
	fmt.Println(maxv)
}
