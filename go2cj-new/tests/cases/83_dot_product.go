package main

import "fmt"

func dotProduct(a []int, b []int) int {
	s := 0
	n := len(a)
	for i := 0; i < n; i++ {
		s = s + a[i]*b[i]
	}
	return s
}

func main() {
	a := []int{1, 2, 3}
	b := []int{4, 5, 6}
	fmt.Println(dotProduct(a, b))
	c := []int{0, 0, 0}
	fmt.Println(dotProduct(a, c))
}
