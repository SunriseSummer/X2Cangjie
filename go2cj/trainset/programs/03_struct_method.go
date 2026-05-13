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
	p := Point{X: 3, Y: 4}
	fmt.Println(p.Sum())
}
