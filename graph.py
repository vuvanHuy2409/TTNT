# graph.py
import math
from collections import defaultdict

class Graph:
    def __init__(self):
        self.edges = defaultdict(list)  # {u: [(v, w), ...]}
        self.nodes = {}  # {name: (lat, lon)}

    def add_node(self, name, lat, lon):
        self.nodes[name] = (lat, lon)

    def add_edge(self, u, v, w):
        self.edges[u].append((v, w))
        self.edges[v].append((u, w))

    # --- HÀM CLEAR (QUAN TRỌNG ĐỂ SỬA LỖI CỦA BẠN) ---
    def clear(self):
        """Xóa sạch dữ liệu node và edge cũ"""
        self.edges.clear()
        self.nodes.clear()

    # --- CÁC HÀM ĐÁNH GIÁ (HEURISTIC) ---

    def heuristic_haversine(self, a, b):
        """1. Haversine: Khoảng cách chim bay thực tế (Chính xác nhất trên bản đồ)"""
        if a not in self.nodes or b not in self.nodes: return 0
        lat1, lon1 = self.nodes[a]
        lat2, lon2 = self.nodes[b]
        R = 6371  # Bán kính trái đất (km)
        dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        val = (math.sin(dlat / 2)**2 +
               math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
        c = 2 * math.atan2(math.sqrt(val), math.sqrt(1 - val))
        return R * c

    def heuristic_manhattan(self, a, b):
        """2. Manhattan (Giả lập): Đi theo dạng bàn cờ (Ziczac).
        Quy đổi 1 độ lat/lon ~ 111km."""
        if a not in self.nodes or b not in self.nodes: return 0
        lat1, lon1 = self.nodes[a]
        lat2, lon2 = self.nodes[b]
        # |dx| + |dy|
        d_lat = abs(lat1 - lat2) * 111
        d_lon = abs(lon1 - lon2) * 111
        return d_lat + d_lon

    def heuristic_dijkstra(self, a, b):
        """3. Dijkstra: Coi h(n) = 0. Thuật toán sẽ chỉ dựa vào g(n)."""
        return 0