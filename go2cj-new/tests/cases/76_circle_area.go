package main

import "fmt"

type Circle struct {
	R int
}

func areaTimes100(c Circle) int {
	return 314 * c.R * c.R
}

func main() {
	c1 := Circle{R: 1}
	c2 := Circle{R: 5}
	fmt.Println(areaTimes100(c1))
	fmt.Println(areaTimes100(c2))
}
