from __future__ import annotations

from itertools import combinations

from app.algorithms.graph import Graph


def _pairwise_cost_table(
    graph: Graph, stops: list[str], strategy: str, transport_mode: str
) -> dict[tuple[str, str], float]:
    costs: dict[tuple[str, str], float] = {}
    for source in stops:
        dist = graph.shortest_distances(source, strategy=strategy, transport_mode=transport_mode)
        for target in stops:
            if source == target:
                costs[(source, target)] = 0.0
            else:
                costs[(source, target)] = dist.get(target, float("inf"))
    return costs


def _route_cost(route: list[str], costs: dict[tuple[str, str], float]) -> float:
    total = 0.0
    for source, target in zip(route, route[1:]):
        edge_cost = costs.get((source, target), float("inf"))
        if edge_cost == float("inf"):
            return float("inf")
        total += edge_cost
    return total


def held_karp(
    graph: Graph, start: str, nodes: list[str], strategy: str, transport_mode: str
) -> tuple[list[str], float]:
    unique_nodes = [node for node in dict.fromkeys(nodes) if node != start]
    if not unique_nodes:
        return [start, start], 0.0

    all_nodes = [start] + unique_nodes
    costs = _pairwise_cost_table(graph, all_nodes, strategy, transport_mode)

    dp: dict[tuple[frozenset[str], str], tuple[float, str | None]] = {}
    for node in unique_nodes:
        dp[(frozenset([node]), node)] = (costs[(start, node)], start)

    for size in range(2, len(unique_nodes) + 1):
        for subset in combinations(unique_nodes, size):
            subset_set = frozenset(subset)
            for last in subset:
                prev_subset = subset_set - {last}
                best = (float("inf"), None)
                for prev in prev_subset:
                    prev_cost, _ = dp[(prev_subset, prev)]
                    candidate = prev_cost + costs[(prev, last)]
                    if candidate < best[0]:
                        best = (candidate, prev)
                dp[(subset_set, last)] = best

    final_subset = frozenset(unique_nodes)
    best_cost = float("inf")
    best_last: str | None = None
    for node in unique_nodes:
        tour_cost = dp[(final_subset, node)][0] + costs[(node, start)]
        if tour_cost < best_cost:
            best_cost = tour_cost
            best_last = node

    if best_last is None or best_cost == float("inf"):
        return [start], float("inf")

    ordered = [start]
    subset = final_subset
    current: str | None = best_last
    trail = []
    while current is not None and subset:
        trail.append(current)
        _, prev = dp[(subset, current)]
        subset = subset - {current}
        current = None if prev in {None, start} else prev
    ordered.extend(reversed(trail))
    ordered.append(start)
    return ordered, best_cost


def nearest_neighbor_two_opt(
    graph: Graph, start: str, nodes: list[str], strategy: str, transport_mode: str
) -> tuple[list[str], float]:
    unique_nodes = [node for node in dict.fromkeys(nodes) if node != start]
    if not unique_nodes:
        return [start, start], 0.0

    all_stops = [start] + unique_nodes
    costs = _pairwise_cost_table(graph, all_stops, strategy, transport_mode)

    remaining = set(unique_nodes)
    route = [start]
    current = start
    while remaining:
        next_node = min(
            remaining,
            key=lambda node: costs[(current, node)],
        )
        route.append(next_node)
        remaining.remove(next_node)
        current = next_node
    route.append(start)

    best_route = route
    best_cost = _route_cost(best_route, costs)

    improved = True
    while improved:
        improved = False
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                left_source, left_target = best_route[i - 1], best_route[i]
                right_source, right_target = best_route[j], best_route[j + 1]
                current_links = costs[(left_source, left_target)] + costs[(right_source, right_target)]
                swapped_links = costs[(left_source, right_source)] + costs[(left_target, right_target)]
                if swapped_links + 1e-9 < current_links:
                    best_route[i : j + 1] = reversed(best_route[i : j + 1])
                    best_cost = _route_cost(best_route, costs)
                    improved = True
                    break
            if improved:
                break

    return best_route, best_cost
