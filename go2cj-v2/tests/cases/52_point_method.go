package main

import "fmt"

type Point struct {
	X int
	Y int
}

func (p Point) Sum() int {
	return p.X + p.Y
}

func main() {
	p := Point{X: 10, Y: 20}
	fmt.Println(p.X)
	fmt.Println(p.Y)
	fmt.Println(p.Sum())
}
