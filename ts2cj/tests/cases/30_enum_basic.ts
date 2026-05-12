enum Direction { North, South, East, West }

function describe(d: Direction): string {
    switch (d) {
        case Direction.North: return "up";
        case Direction.South: return "down";
        case Direction.East:  return "right";
        case Direction.West:  return "left";
    }
    return "?";
}

console.log(describe(Direction.North));
console.log(describe(Direction.East));
