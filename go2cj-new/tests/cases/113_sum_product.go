package main

import "fmt"

func sumProduct(xs []int) (int, int) {
	s := 0
	p := 1
	for _, v := range xs {
		s = s + v
		p = p * v
	}
	return s, p
}

func main() {
	xs := []int{1, 2, 3, 4}
	s, p := sumProduct(xs)
	fmt.Println(s)
	fmt.Println(p)
}
