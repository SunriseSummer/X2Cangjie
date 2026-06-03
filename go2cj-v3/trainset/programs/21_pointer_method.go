package main

import "fmt"

type Counter struct {
	count int
}

func (c *Counter) Inc() {
	c.count++
}

func (c *Counter) Get() int {
	return c.count
}

func main() {
	c := &Counter{}
	for i := 0; i < 5; i++ {
		c.Inc()
	}
	fmt.Println(c.Get())
	c.Inc()
	c.Inc()
	fmt.Println(c.Get())
}
