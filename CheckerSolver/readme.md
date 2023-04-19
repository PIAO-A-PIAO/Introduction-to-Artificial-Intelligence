The utility for terminal state is 200 for winning and 0 for losing. The reason I didn’t use infinity
and negative infinity is that the range of all non-terminal states is between 30 and 70.

For non-terminal states, there are several things I considered:

1. The base value is 50 for every board
2. For every red pawn, add 3; for every black pawn, minus 3
3. For every red king, add 6; for every black king, minus3
4. Closer the red pawn to black end, more credits added: + (7-x_coord)
5. Closer the blue pawn to red end, more credits minused -(x_coord)
6. If there are blue pawns that can be captured by multiple jump, add 2 for each neighbor
7. If there are red pawns that can be captured by multiple jump, minus 2 for each neighbor

Node ordering is based on the evaluated value of current nodes instead of actual utility values
returned by their children. This is because the actual value of a middle node is not known until
its leaves are searched.

I also used state caching to avoid repetition in searching. For each explored state, I hash it into
cache based on pieces and their positions.