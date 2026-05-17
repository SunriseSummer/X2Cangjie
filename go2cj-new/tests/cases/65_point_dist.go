package main

import "fmt"

type Point struct {
	X int
	Y int
}

func distSq(a Point, b Point) int {
	dx := a.X - b.X
	dy := a.Y - b.Y
	return dx*dx + dy*dy
}

func main() {
	p := Point{X: 0, Y: 0}
	q := Point{X: 3, Y: 4}
	fmt.Println(distSq(p, q))
	r := Point{X: 1, Y: 1}
	fmt.Println(distSq(p, r))
}
