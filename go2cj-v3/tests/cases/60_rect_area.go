package main

import "fmt"

type Rect struct {
	W int
	H int
}

func (r Rect) Area() int { return r.W * r.H }

func main() {
	r := Rect{W: 4, H: 6}
	fmt.Println(r.Area())
}
