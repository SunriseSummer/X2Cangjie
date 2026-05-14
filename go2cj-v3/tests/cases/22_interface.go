package main

import "fmt"

type Greeter interface {
Greet() string
}

type English struct{}

func (e English) Greet() string {
return "Hello"
}

func main() {
var g Greeter = English{}
fmt.Println(g.Greet())
}
