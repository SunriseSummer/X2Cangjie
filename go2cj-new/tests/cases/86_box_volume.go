package main

import "fmt"

type Box struct {
	W int
	H int
	D int
}

func volume(b Box) int {
	return b.W * b.H * b.D
}

func main() {
	a := Box{W: 2, H: 3, D: 4}
	b := Box{W: 5, H: 5, D: 5}
	fmt.Println(volume(a))
	fmt.Println(volume(b))
}
