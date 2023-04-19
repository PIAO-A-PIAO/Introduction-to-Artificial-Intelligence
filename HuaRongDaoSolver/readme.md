Before showing the advanced heuristic function, let’s first define some functions:

1) manhattan_dist(goal_piece, goal_position): Manhattan distance between the goal piece
and the goal position. This is the sum of the differences in the x and y coordinates of
their top left corners. For example, when the goal piece has coordinates (0, 1), the
Manhattan distance would be |0-1|+|1-3| = 3.

2) box_between(goal_piece, empty_space): Number of boxes on the shortest path from an
empty space to an edge of the goal piece. For example, the goal piece is at (1, 1), (2, 1),
(1, 2), and (2, 2) are also part of the goal piece. When an empty space is at (0, 2), the
function value is 0; when another empty space is at (3, 4), the function value is 2.
3) min_cost(box_between): Lowest possible cost to move an empty space through
box_between many boxes. In Huarongdao, an empty space can move through at most
two boxes by sliding a 1x2 piece, so at least min_cost = ceil(box_between / 2) steps are
required.

For example, 0 moves are needed if the empty space is adjacent to the goal piece (0
boxes in between), at least 1 move is needed when the empty space is 1 or 2 boxes
away, and at least 2 moves are needed when the empty space is 3 or 4 boxes away.
Based on the definitions above, we have the advanced heuristic function:
h(state) = manhattan_dist(goal_piece, goal_position) + min_cost (max(box_between(goal_piece, empty1), box_between(goal_piece, empty2)))
 
The advanced heuristic function is the Manhattan distance between the goal piece and the goal
position plus the least possible cost to make the farther empty space adjacent to the goal piece.
The advanced heuristic function is admissible because it never overestimates the cost of
reaching the goal. Manhattan distance provides the least cost of moving the goal piece, and the
min_cost function provides the least cost of making the goal piece prepared to move (because
the goal piece can move only if both empty spaces are adjacent to it). Therefore, the estimate
will never exceed the actual cost.

The advanced heuristic function dominates the Manhattan distance. Since the first part is
exactly the Manhattan distance, and the second part is greater than or equal to 0, the advanced
heuristic value is always greater than or equal to the Manhattan distance.
