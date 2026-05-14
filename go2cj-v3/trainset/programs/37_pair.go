package main

import "fmt"

type Pair struct {
	A int
	B int
}

func main() {
	p := Pair{A: 7, B: 8}
	fmt.Println(p.A)
	fmt.Println(p.B)
	fmt.Println(p.A + p.B)
}
