package main

import "fmt"

func sumSlice(xs []int) int {
	s := 0
	for _, v := range xs {
		s = s + v
	}
	return s
}

func avg(xs []int) int {
	if len(xs) == 0 {
		return 0
	}
	return sumSlice(xs) / len(xs)
}

func main() {
	xs := []int{1, 2, 3, 4, 5}
	fmt.Println(sumSlice(xs))
	fmt.Println(avg(xs))
	ys := []int{10, 20, 30}
	fmt.Println(avg(ys))
}
