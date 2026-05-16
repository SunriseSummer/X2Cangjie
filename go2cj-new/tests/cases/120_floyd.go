package main

import "fmt"

func floydShortestPaths(n int, edges [][]int) [][]int {
	const INF = 1000000
	dist := make([][]int, n)
	for i := 0; i < n; i++ {
		dist[i] = make([]int, n)
		for j := 0; j < n; j++ {
			if i == j {
				dist[i][j] = 0
			} else {
				dist[i][j] = INF
			}
		}
	}
	for _, e := range edges {
		dist[e[0]][e[1]] = e[2]
	}
	for k := 0; k < n; k++ {
		for i := 0; i < n; i++ {
			for j := 0; j < n; j++ {
				cand := dist[i][k] + dist[k][j]
				if cand < dist[i][j] {
					dist[i][j] = cand
				}
			}
		}
	}
	return dist
}

func main() {
	n := 4
	edges := [][]int{
		{0, 1, 5},
		{0, 3, 10},
		{1, 2, 3},
		{2, 3, 1},
	}
	d := floydShortestPaths(n, edges)
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			fmt.Println(d[i][j])
		}
	}
}
