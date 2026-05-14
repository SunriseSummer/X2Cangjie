package main

import "fmt"

type Counter struct {
	count int
}

func (c *Counter) Inc() {
	c.count++
}

func (c Counter) Get() int {
	return c.count
}

func main() {
	c := Counter{count: 0}
	c.Inc()
	c.Inc()
	c.Inc()
	fmt.Println(c.Get())
}
