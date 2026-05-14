package main

import "fmt"

type Rectangle struct {
W int
H int
}

func (r Rectangle) Area() int {
return r.W * r.H
}

func main() {
r := Rectangle{W: 4, H: 5}
fmt.Println(r.Area())
xs := []int{1, 2, 3}
total := 0
for _, v := range xs {
total += v
}
fmt.Println(total)
}
