package main

import "fmt"

func main() {
	xs := []int{1, 2, 3, 4, 5}
	ys := []int{}
	for _, v := range xs {
		ys = append(ys, v*v)
	}
	for _, v := range ys {
		fmt.Println(v)
	}
}
