package main

import "fmt"

type Rect struct {
	W, H int
}

func (r Rect) Area() int      { return r.W * r.H }
func (r Rect) Perimeter() int { return 2 * (r.W + r.H) }

type Circle struct {
	R int
}

func (c Circle) Area() int      { return 3 * c.R * c.R }
func (c Circle) Perimeter() int { return 6 * c.R }

func main() {
	r := Rect{W: 3, H: 4}
	c := Circle{R: 5}
	fmt.Println(r.Area())
	fmt.Println(r.Perimeter())
	fmt.Println(c.Area())
	fmt.Println(c.Perimeter())
}
