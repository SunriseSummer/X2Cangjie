package main

import "fmt"

type Animal interface {
	Sound() string
	Name() string
}

type Dog struct {
	name string
}

func (d Dog) Sound() string { return "Woof" }
func (d Dog) Name() string  { return d.name }

type Cat struct {
	name string
}

func (c Cat) Sound() string { return "Meow" }
func (c Cat) Name() string  { return c.name }

func describe(a Animal) {
	fmt.Println(a.Name() + " says " + a.Sound())
}

func main() {
	describe(Dog{name: "Rex"})
	describe(Cat{name: "Whiskers"})
}
