package main

import "fmt"

type Animal interface {
	Sound() string
}

type Dog struct {
	name string
}

func (d Dog) Sound() string {
	return "woof"
}

type Cat struct {
	name string
}

func (c Cat) Sound() string {
	return "meow"
}

func main() {
	var a Animal
	a = Dog{name: "rex"}
	fmt.Println(a.Sound())
	a = Cat{name: "whiskers"}
	fmt.Println(a.Sound())
}
