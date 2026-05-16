package main

import "fmt"

type Counter struct {
	Value int
}

func (c Counter) Get() int {
	return c.Value
}

func main() {
	c := Counter{Value: 42}
	fmt.Println(c.Get())
}
