package main

import "fmt"

type Animal interface {
	Sound() string
	Name() string
}

type Dog struct {
	name string
}

func (d Dog) Sound() string {
	return "woof"
}

func (d Dog) Name() string {
	return d.name
}

func describe(a Animal) {
	fmt.Println(a.Name(), a.Sound())
}

func main() {
	describe(Dog{name: "Rex"})
}
