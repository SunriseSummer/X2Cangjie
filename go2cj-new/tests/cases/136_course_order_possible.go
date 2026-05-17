package main

import "fmt"

func canFinish(num int, prereq [][]int) bool {
g := make([][]int, num)
indeg := make([]int, num)
for _, p := range prereq {
a, b := p[0], p[1]
g[b] = append(g[b], a)
indeg[a]++
}
q := []int{}
for i := 0; i < num; i++ {
if indeg[i] == 0 {
q = append(q, i)
}
}
seen := 0
for head := 0; head < len(q); head++ {
u := q[head]
seen++
for _, v := range g[u] {
indeg[v]--
if indeg[v] == 0 {
q = append(q, v)
}
}
}
return seen == num
}

func main() {
fmt.Println(canFinish(2, [][]int{{1, 0}}))
fmt.Println(canFinish(2, [][]int{{1, 0}, {0, 1}}))
fmt.Println(canFinish(4, [][]int{{1, 0}, {2, 0}, {3, 1}, {3, 2}}))
}
