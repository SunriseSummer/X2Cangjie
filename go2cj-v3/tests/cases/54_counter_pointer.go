package main

import "fmt"

type Counter struct {
	count int
}

func (c *Counter) Inc() {
	c.count++
}

func main() {
	c := &Counter{}
	c.Inc()
	c.Inc()
	c.Inc()
	fmt.Println(c.count)
}
