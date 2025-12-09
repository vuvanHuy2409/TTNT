# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import tkintermapview

# --- IMPORT MODULES ---
# Đảm bảo bạn đã có file graph.py và algorithms.py cùng thư mục
from graph import Graph
from algorithms import greedy_search, a_star_search, reconstruct_path


class MapRoutingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Tìm Đường Thông Minh (Multi-Layer Map)")
        self.root.geometry("1350x850")

        self.graph = Graph()
        self.markers = {}  # Quản lý các điểm trên bản đồ
        self.paths = []  # Quản lý các đường vẽ kết quả tìm kiếm
        self.base_paths = []  # Quản lý các đường nối cơ sở (màu đen)
        self.current_mode = "Vinhomes"  # Mặc định

        self.create_widgets()

        # Khởi tạo dữ liệu mặc định
        self.load_data_by_mode()

    def create_widgets(self):
        # --- Panel Trái (Điều khiển) ---
        left_panel = tk.Frame(self.root, width=420, bg="white", padx=15, pady=15)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # 1. Header & Switch Mode
        tk.Label(left_panel, text="BẢN ĐỒ ĐỊNH VỊ", font=("Segoe UI", 18, "bold"), bg="white", fg="#b91c1c").pack(
            pady=(5, 10))

        tk.Label(left_panel, text="Chọn hệ thống cửa hàng:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.mode_var = tk.StringVar(value="Vinhomes")
        frm_mode = tk.Frame(left_panel, bg="white")
        frm_mode.pack(fill=tk.X, pady=5)

        # Radio buttons để chuyển đổi
        rb1 = tk.Radiobutton(frm_mode, text="Khu đô thị Vinhomes", variable=self.mode_var, value="Vinhomes",
                             bg="white", font=("Segoe UI", 10), command=self.on_mode_switch)
        rb1.pack(side=tk.LEFT, padx=5)

        rb2 = tk.Radiobutton(frm_mode, text="Chuỗi KFC Hà Nội", variable=self.mode_var, value="KFC",
                             bg="white", font=("Segoe UI", 10), command=self.on_mode_switch)
        rb2.pack(side=tk.LEFT, padx=5)

        tk.Frame(left_panel, height=2, bg="#e5e7eb").pack(fill=tk.X, pady=15)  # Dòng kẻ ngang

        # 2. Chọn điểm Đi/Đến
        frm_sel = tk.Frame(left_panel, bg="white")
        frm_sel.pack(fill=tk.X, pady=5)

        tk.Label(frm_sel, text="Bắt đầu:", bg="white").grid(row=0, column=0, sticky="w")
        self.start_var = tk.StringVar()
        self.cb_start = ttk.Combobox(frm_sel, textvariable=self.start_var, state="readonly", width=32)
        self.cb_start.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frm_sel, text="Kết thúc:", bg="white").grid(row=1, column=0, sticky="w")
        self.goal_var = tk.StringVar()
        self.cb_goal = ttk.Combobox(frm_sel, textvariable=self.goal_var, state="readonly", width=32)
        self.cb_goal.grid(row=1, column=1, padx=5, pady=5)

        # 3. Cấu hình thuật toán
        tk.Label(left_panel, text="Cấu hình A* / Greedy:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w",
                                                                                                           pady=(20, 5))

        self.algo_var = tk.StringVar(value="A*")
        frm_algo = tk.Frame(left_panel, bg="white")
        frm_algo.pack(anchor="w")
        tk.Radiobutton(frm_algo, text="A* (Chính xác)", variable=self.algo_var, value="A*", bg="white").pack(
            side=tk.LEFT, padx=5)
        tk.Radiobutton(frm_algo, text="Greedy (Nhanh)", variable=self.algo_var, value="Greedy", bg="white").pack(
            side=tk.LEFT, padx=5)

        tk.Label(left_panel, text="Hàm đánh giá (Heuristic):", bg="white").pack(anchor="w", pady=(5, 0))
        self.heu_map = {
            "Haversine (Chim bay - Chuẩn)": self.graph.heuristic_haversine,
            "Manhattan (Giả lập phố vuông)": self.graph.heuristic_manhattan,
            "Dijkstra (h=0)": self.graph.heuristic_dijkstra
        }
        self.heu_var = tk.StringVar(value="Haversine (Chim bay - Chuẩn)")
        ttk.Combobox(left_panel, textvariable=self.heu_var, values=list(self.heu_map.keys()), state="readonly",
                     width=35).pack(fill=tk.X)

        # 4. Nút bấm
        tk.Button(left_panel, text="TÌM ĐƯỜNG", bg="#dc2626", fg="white", font=("Segoe UI", 12, "bold"), pady=8,
                  command=self.run_search).pack(fill=tk.X, pady=20)

        # 5. Kết quả
        tk.Label(left_panel, text="Phân tích chi tiết:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        # [CẬP NHẬT] Đã tăng font size lên 13
        self.txt_result = tk.Text(left_panel, height=18, font=("Consolas", 13), bg="#f8fafc", padx=8, pady=8)
        self.txt_result.pack(fill=tk.BOTH, expand=True, pady=5)

        # --- Panel Phải (Bản đồ) ---
        right_panel = tk.Frame(self.root)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.map_widget = tkintermapview.TkinterMapView(right_panel, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=vi&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(21.0285, 105.8542)  # Tâm Hà Nội
        self.map_widget.set_zoom(12)

    def on_mode_switch(self):
        """Hàm xử lý khi người dùng đổi chế độ (Vinhomes <-> KFC)"""
        new_mode = self.mode_var.get()
        if new_mode == self.current_mode: return

        self.current_mode = new_mode
        self.load_data_by_mode()

    def load_data_by_mode(self):
        # 1. Xóa sạch dữ liệu cũ
        self.graph.clear()  # Xóa node/edge trong logic
        self.map_widget.delete_all_marker()  # Xóa marker trên bản đồ

        # Xóa các đường vẽ kết quả
        for p in self.paths: p.delete()
        self.paths.clear()

        # Xóa các đường nối cơ sở (màu đen)
        for p in self.base_paths: p.delete()
        self.base_paths.clear()

        self.markers.clear()
        self.txt_result.delete("1.0", tk.END)

        # 2. Nạp dữ liệu mới
        if self.current_mode == "Vinhomes":
            self.setup_vinhomes_data()
            color = "#0f766e"  # Xanh cổ vịt
        else:
            self.setup_kfc_data()
            color = "#b91c1c"  # Đỏ thương hiệu KFC

        # 3. Vẽ lại các điểm cơ sở và cập nhật Combobox
        self.draw_base_graph(marker_color=color)

        # Cập nhật danh sách điểm cho Combobox
        locations = sorted(list(self.graph.nodes.keys()))
        self.cb_start['values'] = locations
        self.cb_goal['values'] = locations

        if len(locations) >= 2:
            self.start_var.set(locations[0])
            self.goal_var.set(locations[1])
        else:
            self.start_var.set("")
            self.goal_var.set("")

    # --- DỮ LIỆU DATASET 1: VINHOMES ---
    def setup_vinhomes_data(self):
        vinhomes_locations = [
            ("Vinhomes Royal City", 21.0028, 105.8139), ("Vinhomes Times City", 20.9954, 105.8679),
            ("Vinhomes Riverside", 21.0485, 105.9170), ("Vinhomes Metropolis", 21.0315, 105.8125),
            ("Vinhomes Nguyen Chi Thanh", 21.0236, 105.8118), ("Vinhomes Gardenia", 21.0372, 105.7628),
            ("Vinhomes Skylake", 21.0210, 105.7830), ("Vinhomes Green Bay", 21.0062, 105.7875),
            ("Vinhomes Smart City", 21.0084, 105.7369), ("Vinhomes Ocean Park", 21.0000, 105.9550),
            ("Vinhomes Symphony", 21.0450, 105.9120)
        ]
        self.build_graph_from_list(vinhomes_locations, connect_radius=10.0)

    # --- DỮ LIỆU DATASET 2: KFC ---
    def setup_kfc_data(self):
        kfc_locations = [
            ("KFC Hoan Kiem", 21.0287, 105.8524), ("KFC Ba Trieu", 21.0125, 105.8510),
            ("KFC Tay Son", 21.0076, 105.8236), ("KFC Chua Lang", 21.0239, 105.8005),
            ("KFC Cau Giay", 21.0352, 105.7937), ("KFC Pham Ngoc Thach", 21.0063, 105.8327),
            ("KFC Bach Mai", 21.0021, 105.8507), ("KFC Aeon Long Bien", 21.0279, 105.8953),
            ("KFC BigC Thang Long", 21.0075, 105.7925), ("KFC Nguyen Van Cu", 21.0432, 105.8752),
            ("KFC Times City", 20.9956, 105.8670), ("KFC Royal City", 21.0030, 105.8135),
            ("KFC Hoang Quoc Viet", 21.0461, 105.7920), ("KFC My Dinh", 21.0205, 105.7705),
            ("KFC Ha Dong", 20.9705, 105.7801)
        ]
        # KFC mật độ dày hơn, bán kính kết nối nhỏ hơn (6km) để tạo đồ thị phức tạp hơn
        self.build_graph_from_list(kfc_locations, connect_radius=6.0)

    def build_graph_from_list(self, data_list, connect_radius):
        """Hàm chung để tạo Node và Edge từ danh sách tọa độ"""
        # 1. Thêm Nodes
        for name, lat, lon in data_list:
            self.graph.add_node(name, lat, lon)

        # 2. Tạo Edges (Nối nếu khoảng cách < radius)
        node_names = list(self.graph.nodes.keys())
        for i in range(len(node_names)):
            for j in range(i + 1, len(node_names)):
                u, v = node_names[i], node_names[j]
                dist_km = self.graph.heuristic_haversine(u, v)

                if dist_km < connect_radius:
                    # Giả lập đường thực tế vòng vèo (hệ số 1.4)
                    road_weight = dist_km * 1.4
                    self.graph.add_edge(u, v, round(road_weight, 2))

    def draw_base_graph(self, marker_color):
        # Vẽ Markers
        for name, (lat, lon) in self.graph.nodes.items():
            self.markers[name] = self.map_widget.set_marker(lat, lon, text=name,
                                                            marker_color_circle="white",
                                                            marker_color_outside=marker_color,
                                                            font=("Arial", 9, "bold"))
        # Vẽ Edges mờ
        drawn = set()
        for u in self.graph.edges:
            for v, w in self.graph.edges[u]:
                if tuple(sorted((u, v))) in drawn: continue
                drawn.add(tuple(sorted((u, v))))
                la, lo = self.graph.nodes[u]
                lb, lo2 = self.graph.nodes[v]

                # [CẬP NHẬT] Đã đổi màu đường dẫn thành ĐEN (black)
                path_obj = self.map_widget.set_path([(la, lo), (lb, lo2)], color="black", width=1)
                self.base_paths.append(path_obj)

    def run_search(self):
        s, g = self.start_var.get(), self.goal_var.get()
        if not s or not g or s == g:
            messagebox.showwarning("Lỗi", "Vui lòng chọn điểm đi và đến hợp lệ.")
            return

        # Xóa đường kết quả cũ (nhưng giữ đường cơ sở màu đen)
        for p in self.paths: p.delete()
        self.paths.clear()
        self.txt_result.delete("1.0", tk.END)

        h_func = self.heu_map[self.heu_var.get()]
        algo = self.algo_var.get()

        # Chạy thuật toán
        if algo == "A*":
            came_from, cost_so_far = a_star_search(self.graph, s, g, h_func)
            color = "#10b981"  # Xanh lá A*
        else:
            came_from, cost_so_far = greedy_search(self.graph, s, g, h_func)
            color = "#f59e0b"  # Vàng cam Greedy

        path = reconstruct_path(came_from, s, g)

        # Hiển thị kết quả
        self.txt_result.insert(tk.END, f"BẢN ĐỒ: {self.current_mode.upper()}\n")
        self.txt_result.insert(tk.END, f"Thuật toán: {algo} | {self.heu_var.get()}\n")
        self.txt_result.insert(tk.END, "-" * 45 + "\n")

        if not path:
            self.txt_result.insert(tk.END, "Không tìm thấy đường đi!\n(Các điểm quá xa, không có kết nối)")
            return

        total_cost = cost_so_far[g]
        self.txt_result.insert(tk.END, f"Tổng chi phí ước tính: {total_cost:.2f}\n\n")
        self.txt_result.insert(tk.END, f"{'Địa điểm':<20} | {'f':<6} = {'g':<6} + {'h':<6}\n")
        self.txt_result.insert(tk.END, "-" * 45 + "\n")

        path_coords = []
        for node in path:
            path_coords.append(self.graph.nodes[node])
            g_val = cost_so_far[node]
            h_val = h_func(node, g)
            f_val = g_val + h_val

            # Cắt tên cho ngắn gọn
            name_disp = node.replace("Vinhomes ", "").replace("KFC ", "")
            name_disp = (name_disp[:18] + '..') if len(name_disp) > 18 else name_disp

            if algo == "Greedy":
                self.txt_result.insert(tk.END, f"{name_disp:<20} | h={h_val:.2f}\n")
            else:
                self.txt_result.insert(tk.END, f"{name_disp:<20} | {f_val:.1f}  = {g_val:.1f}  + {h_val:.1f}\n")

        # Vẽ đường kết quả (đè lên đường đen)
        path_obj = self.map_widget.set_path(path_coords, color=color, width=5)
        self.paths.append(path_obj)


if __name__ == "__main__":
    root = tk.Tk()
    app = MapRoutingApp(root)
    root.mainloop()