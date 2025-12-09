# algorithms.py
import heapq


def greedy_search(graph, start, goal, h_func):
    """Greedy chỉ quan tâm h(n)"""
    if start not in graph.nodes or goal not in graph.nodes:
        return {}, {}
    # Sử dụng hàm h_func được truyền vào
    frontier = [(h_func(start, goal), start)]
    came_from = {start: None}
    cost_so_far = {start: 0}  # Greedy không dùng cái này để chọn đường, nhưng vẫn tính để hiển thị

    visited = set()
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        if current in visited:
            continue
        visited.add(current)
        for neighbor, weight in graph.edges.get(current, []):
            if neighbor not in came_from:
                # Priority chỉ là h(n)
                priority = h_func(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current
                cost_so_far[neighbor] = cost_so_far[current] + weight
    return came_from, cost_so_far


def a_star_search(graph, start, goal, h_func):
    """A* quan tâm f(n) = g(n) + h(n)"""
    if start not in graph.nodes or goal not in graph.nodes:
        return {}, {}

    # Priority = f(n), g_score, node
    frontier = [(h_func(start, goal), 0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current_cost, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor, weight in graph.edges.get(current, []):
            new_cost = cost_so_far[current] + weight
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                # f(n) = g(n) + h(n)
                # Sử dụng hàm h_func được truyền vào
                h_val = h_func(neighbor, goal)
                priority = new_cost + h_val
                heapq.heappush(frontier, (priority, new_cost, neighbor))
                came_from[neighbor] = current

    return came_from, cost_so_far


def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return None
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None: return None
    path.append(start)
    path.reverse()
    return path