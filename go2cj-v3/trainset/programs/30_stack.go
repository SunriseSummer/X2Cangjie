package main

import "fmt"

type Stack struct {
	items []int
}

func (s *Stack) Push(v int) {
	s.items = append(s.items, v)
}

func (s *Stack) Pop() int {
	n := len(s.items)
	v := s.items[n-1]
	s.items = s.items[:n-1]
	return v
}

func (s *Stack) Size() int {
	return len(s.items)
}

func main() {
	s := &Stack{}
	s.Push(10)
	s.Push(20)
	s.Push(30)
	fmt.Println(s.Size())
	fmt.Println(s.Pop())
	fmt.Println(s.Pop())
	fmt.Println(s.Size())
}
