package main

import "fmt"

type Vec struct {
	X int
	Y int
	Z int
}

func dotV(a Vec, b Vec) int {
	return a.X*b.X + a.Y*b.Y + a.Z*b.Z
}

func main() {
	a := Vec{X: 1, Y: 2, Z: 3}
	b := Vec{X: 4, Y: 5, Z: 6}
	fmt.Println(dotV(a, b))
}
