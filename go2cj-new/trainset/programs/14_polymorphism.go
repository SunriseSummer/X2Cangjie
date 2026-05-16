package main

import "fmt"

type Animal interface {
	Sound() string
}

type Dog struct{ name string }
type Cat struct{ name string }

func (d Dog) Sound() string { return "woof" }
func (c Cat) Sound() string { return "meow" }

func main() {
	xs := []Animal{Dog{name: "rex"}, Cat{name: "tom"}, Dog{name: "buddy"}}
	for _, a := range xs {
		fmt.Println(a.Sound())
	}
}
