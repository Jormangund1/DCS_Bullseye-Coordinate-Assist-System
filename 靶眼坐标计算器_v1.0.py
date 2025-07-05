import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

class RealTimeBullseyeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("靶眼坐标计算器")
        self.root.geometry("1400x1000")  # 窗口尺寸
        
        # 比例尺设置
        self.scale_options = [9, 30, 60, 90, 120, 240, 360]
        self.current_scale_index = 2  # 默认使用60海里比例尺
        
        # 初始化日志文件
        self.log_file = "bullseye_realtime.log"
        self.init_log_file()
        
        # 创建界面组件
        self.create_widgets()
        
        # 初始计算
        self.calculate()
    
    def init_log_file(self):
        """初始化日志文件"""
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("靶眼坐标计算记录\n")
                    f.write("="*50 + "\n")
                    f.write("时间 | 计算类型 | 输入参数 | 计算结果\n")
                    f.write("-"*90 + "\n")
        except Exception as e:
            messagebox.showerror("错误", f"无法初始化日志文件: {str(e)}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板
        left_frame = ttk.Frame(main_frame, width=800)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 计算模式选择
        mode_frame = ttk.LabelFrame(left_frame, text="计算模式", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.calc_mode = tk.StringVar(value="mode1")
        ttk.Radiobutton(mode_frame, text="模式1: 已知本机和敌机相对本机位置，求敌机靶眼坐标", 
                       variable=self.calc_mode, value="mode1", command=self.calculate).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="模式2: 已知本机和敌机靶眼坐标，求敌机相对本机位置", 
                       variable=self.calc_mode, value="mode2", command=self.calculate).pack(anchor=tk.W)
        
        # 输入部分
        input_frame = ttk.LabelFrame(left_frame, text="输入参数", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 本机信息（共用）
        ttk.Label(input_frame, text="本机相对靶眼方位(度):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ownship_brg = tk.StringVar()
        self.ownship_brg.trace_add("write", lambda *args: self.calculate())
        self.ownship_brg_entry = ttk.Entry(input_frame, textvariable=self.ownship_brg)
        self.ownship_brg_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="本机距离靶眼距离(海里):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ownship_dist = tk.StringVar()
        self.ownship_dist.trace_add("write", lambda *args: self.calculate())
        self.ownship_dist_entry = ttk.Entry(input_frame, textvariable=self.ownship_dist)
        self.ownship_dist_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 模式1特有输入
        self.mode1_frame = ttk.Frame(input_frame)
        ttk.Label(self.mode1_frame, text="敌机相对本机方位(度):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.target_rel_brg = tk.StringVar()
        self.target_rel_brg.trace_add("write", lambda *args: self.calculate())
        self.target_rel_brg_entry = ttk.Entry(self.mode1_frame, textvariable=self.target_rel_brg)
        self.target_rel_brg_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.mode1_frame, text="敌机距离本机距离(海里):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.target_rel_dist = tk.StringVar()
        self.target_rel_dist.trace_add("write", lambda *args: self.calculate())
        self.target_rel_dist_entry = ttk.Entry(self.mode1_frame, textvariable=self.target_rel_dist)
        self.target_rel_dist_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 模式2特有输入
        self.mode2_frame = ttk.Frame(input_frame)
        ttk.Label(self.mode2_frame, text="敌机靶眼方位(度):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.target_brg = tk.StringVar()
        self.target_brg.trace_add("write", lambda *args: self.calculate())
        self.target_brg_entry = ttk.Entry(self.mode2_frame, textvariable=self.target_brg)
        self.target_brg_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(self.mode2_frame, text="敌机距离靶眼距离(海里):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.target_dist = tk.StringVar()
        self.target_dist.trace_add("write", lambda *args: self.calculate())
        self.target_dist_entry = ttk.Entry(self.mode2_frame, textvariable=self.target_dist)
        self.target_dist_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 控制按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="清空", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看日志", command=self.view_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # 结果输出
        result_frame = ttk.LabelFrame(left_frame, text="计算结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(result_frame, text="计算结果:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(left_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=5)
        
        # 右侧雷达图面板
        right_frame = ttk.Frame(main_frame, width=500)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=5)
        
        # 比例尺控制按钮
        scale_control_frame = ttk.Frame(right_frame)
        scale_control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(scale_control_frame, text="放大比例", 
                  command=lambda: self.change_scale("down")).pack(side=tk.LEFT, padx=5)
        ttk.Button(scale_control_frame, text="缩小比例", 
                  command=lambda: self.change_scale("up")).pack(side=tk.LEFT, padx=5)
        
        # 靶眼雷达图（上方）
        bullseye_radar_frame = ttk.LabelFrame(right_frame, text="靶眼雷达图(中心:靶眼)", padding=5)
        bullseye_radar_frame.pack(fill=tk.BOTH, expand=True)
        self.bullseye_canvas = tk.Canvas(bullseye_radar_frame, width=480, height=350, bg="white")
        self.bullseye_canvas.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 本机雷达图（下方）
        ownship_radar_frame = ttk.LabelFrame(right_frame, text="本机雷达图(中心:本机)", padding=5)
        ownship_radar_frame.pack(fill=tk.BOTH, expand=True)
        self.ownship_canvas = tk.Canvas(ownship_radar_frame, width=480, height=350, bg="white")
        self.ownship_canvas.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 初始显示正确的输入框架
        self.update_input_fields()
        self.calc_mode.trace_add('write', lambda *args: self.update_input_fields())
    
    def draw_radar(self, canvas, center_x, center_y, max_radius, current_max_dist, is_bullseye=True):
        """绘制雷达图基础框架"""
        canvas.delete("all")
        circle_count = 3  # 3个同心圆
        
        # 绘制同心圆和距离标签
        for i in range(1, circle_count + 1):
            radius = i * max_radius / circle_count
            distance = i * current_max_dist / circle_count
            canvas.create_oval(center_x - radius, center_y - radius,
                             center_x + radius, center_y + radius,
                             outline="gray", dash=(2,2))
            canvas.create_text(center_x, center_y - radius - 10,
                             text=f"{distance:.0f}nm", fill="blue")
        
        # 绘制角度线(每30度)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            end_x = center_x + max_radius * math.sin(rad)
            end_y = center_y - max_radius * math.cos(rad)
            canvas.create_line(center_x, center_y, end_x, end_y, fill="gray", dash=(2,2))
            
            # 角度标签
            if angle % 30 == 0:
                label_x = center_x + (max_radius + 20) * math.sin(rad)
                label_y = center_y - (max_radius + 20) * math.cos(rad)
                canvas.create_text(label_x, label_y, text=f"{angle}°", fill="blue")
        
        # 绘制中心点
        if is_bullseye:
            # 靶眼雷达图中心
            canvas.create_oval(center_x - 5, center_y - 5,
                             center_x + 5, center_y + 5,
                             fill="red", outline="red")
            canvas.create_text(center_x, center_y + 20,
                             text="靶眼", fill="red")
        else:
            # 本机雷达图中心
            canvas.create_oval(center_x - 5, center_y - 5,
                             center_x + 5, center_y + 5,
                             fill="blue", outline="blue")
            canvas.create_text(center_x, center_y + 20,
                             text="本机", fill="blue")
        
        # 显示当前比例尺
        #scale_text = f"当前比例尺: {current_max_dist}海里 (3圈)"
        #canvas.create_text(center_x, 20, 
        #                 text=scale_text, 
        #                 fill="black", 
        #                 font=("Arial", 10, "bold"))
    
    def draw_aircraft_positions(self):
        """在两个雷达图上绘制飞机位置"""
        inputs = self.validate_input()
        if inputs is None:
            # 清空两个雷达图的飞机位置
            self.draw_radar(self.bullseye_canvas, 
                          self.bullseye_canvas.winfo_width()//2, 
                          self.bullseye_canvas.winfo_height()//2, 
                          min(self.bullseye_canvas.winfo_width(), self.bullseye_canvas.winfo_height())//2 - 30,
                          self.scale_options[self.current_scale_index],
                          True)
            
            self.draw_radar(self.ownship_canvas, 
                          self.ownship_canvas.winfo_width()//2, 
                          self.ownship_canvas.winfo_height()//2, 
                          min(self.ownship_canvas.winfo_width(), self.ownship_canvas.winfo_height())//2 - 30,
                          self.scale_options[self.current_scale_index],
                          False)
            return
        
        mode, ownship_brg, ownship_dist, *rest = inputs
        
        # 靶眼雷达图参数
        bullseye_width = self.bullseye_canvas.winfo_width()
        bullseye_height = self.bullseye_canvas.winfo_height()
        bullseye_center_x = bullseye_width // 2
        bullseye_center_y = bullseye_height // 2
        bullseye_max_radius = min(bullseye_center_x, bullseye_center_y) - 30
        current_max_dist = self.scale_options[self.current_scale_index]
        bullseye_scale = bullseye_max_radius / current_max_dist
        
        # 本机雷达图参数
        ownship_width = self.ownship_canvas.winfo_width()
        ownship_height = self.ownship_canvas.winfo_height()
        ownship_center_x = ownship_width // 2
        ownship_center_y = ownship_height // 2
        ownship_max_radius = min(ownship_center_x, ownship_center_y) - 30
        ownship_scale = ownship_max_radius / current_max_dist
        
        try:
            # 计算本机在靶眼雷达图中的位置
            bullseye_ownship_x = bullseye_center_x + ownship_dist * bullseye_scale * math.sin(math.radians(ownship_brg))
            bullseye_ownship_y = bullseye_center_y - ownship_dist * bullseye_scale * math.cos(math.radians(ownship_brg))
            
            # 绘制靶眼雷达图
            self.draw_radar(self.bullseye_canvas, bullseye_center_x, bullseye_center_y, 
                          bullseye_max_radius, current_max_dist, True)
            
            # 在靶眼雷达图上绘制本机
            self.bullseye_canvas.create_oval(bullseye_ownship_x - 6, bullseye_ownship_y - 6,
                                           bullseye_ownship_x + 6, bullseye_ownship_y + 6,
                                           fill="blue", outline="black")
            self.bullseye_canvas.create_text(bullseye_ownship_x, bullseye_ownship_y - 10,
                                           text="本机", fill="blue")
            
            # 绘制本机雷达图
            self.draw_radar(self.ownship_canvas, ownship_center_x, ownship_center_y, 
                          ownship_max_radius, current_max_dist, False)
            
            # 计算靶眼相对于本机的位置
            bullseye_rel_x = bullseye_center_x - bullseye_ownship_x
            bullseye_rel_y = bullseye_center_y - bullseye_ownship_y
            
            # 转换到本机雷达图坐标系
            ownship_bullseye_x = ownship_center_x + bullseye_rel_x * (ownship_scale/bullseye_scale)
            ownship_bullseye_y = ownship_center_y + bullseye_rel_y * (ownship_scale/bullseye_scale)
            
            self.ownship_canvas.create_oval(ownship_bullseye_x - 5, ownship_bullseye_y - 5,
                                          ownship_bullseye_x + 5, ownship_bullseye_y + 5,
                                          fill="red", outline="red")
            self.ownship_canvas.create_text(ownship_bullseye_x, ownship_bullseye_y + 20,
                                          text="靶眼", fill="red")
            
            if mode == "mode1":
                # 模式1: 已知敌机相对本机位置
                target_rel_brg, target_rel_dist = rest
                
                # 计算敌机在靶眼雷达图中的绝对位置
                bullseye_target_x = bullseye_ownship_x + target_rel_dist * bullseye_scale * math.sin(math.radians(target_rel_brg))
                bullseye_target_y = bullseye_ownship_y - target_rel_dist * bullseye_scale * math.cos(math.radians(target_rel_brg))
                
                # 在靶眼雷达图上绘制敌机
                self.bullseye_canvas.create_oval(bullseye_target_x - 6, bullseye_target_y - 6,
                                               bullseye_target_x + 6, bullseye_target_y + 6,
                                               fill="red", outline="black")
                self.bullseye_canvas.create_text(bullseye_target_x, bullseye_target_y - 10,
                                               text="敌机", fill="red")
                
                # 在靶眼雷达图上绘制连线
                self.bullseye_canvas.create_line(bullseye_ownship_x, bullseye_ownship_y, 
                                                bullseye_target_x, bullseye_target_y,
                                                fill="green", dash=(2,2), arrow=tk.LAST)
                
                # 在本机雷达图上绘制敌机(相对位置)
                ownship_target_x = ownship_center_x + target_rel_dist * ownship_scale * math.sin(math.radians(target_rel_brg))
                ownship_target_y = ownship_center_y - target_rel_dist * ownship_scale * math.cos(math.radians(target_rel_brg))
                
                self.ownship_canvas.create_oval(ownship_target_x - 6, ownship_target_y - 6,
                                              ownship_target_x + 6, ownship_target_y + 6,
                                              fill="red", outline="black")
                self.ownship_canvas.create_text(ownship_target_x, ownship_target_y - 10,
                                              text="敌机", fill="red")
                
                # 在本机雷达图上绘制连线
                self.ownship_canvas.create_line(ownship_center_x, ownship_center_y, 
                                              ownship_target_x, ownship_target_y,
                                              fill="green", dash=(2,2), arrow=tk.LAST)
                
            else:
                # 模式2: 已知敌机靶眼坐标
                target_brg, target_dist = rest
                
                # 计算敌机在靶眼雷达图中的绝对位置
                bullseye_target_x = bullseye_center_x + target_dist * bullseye_scale * math.sin(math.radians(target_brg))
                bullseye_target_y = bullseye_center_y - target_dist * bullseye_scale * math.cos(math.radians(target_brg))
                
                # 在靶眼雷达图上绘制敌机
                self.bullseye_canvas.create_oval(bullseye_target_x - 6, bullseye_target_y - 6,
                                               bullseye_target_x + 6, bullseye_target_y + 6,
                                               fill="red", outline="black")
                self.bullseye_canvas.create_text(bullseye_target_x, bullseye_target_y - 10,
                                               text="敌机", fill="red")
                
                # 在靶眼雷达图上绘制连线
                self.bullseye_canvas.create_line(bullseye_ownship_x, bullseye_ownship_y, 
                                                bullseye_target_x, bullseye_target_y,
                                                fill="green", dash=(2,2), arrow=tk.LAST)
                
                # 计算敌机相对于本机的位置
                rel_x = bullseye_target_x - bullseye_ownship_x
                rel_y = bullseye_target_y - bullseye_ownship_y
                
                # 在本机雷达图上绘制敌机(相对位置)
                ownship_target_x = ownship_center_x + rel_x * (ownship_scale/bullseye_scale)
                ownship_target_y = ownship_center_y + rel_y * (ownship_scale/bullseye_scale)
                
                self.ownship_canvas.create_oval(ownship_target_x - 6, ownship_target_y - 6,
                                              ownship_target_x + 6, ownship_target_y + 6,
                                              fill="red", outline="black")
                self.ownship_canvas.create_text(ownship_target_x, ownship_target_y - 10,
                                              text="敌机", fill="red")
                
                # 在本机雷达图上绘制连线
                self.ownship_canvas.create_line(ownship_center_x, ownship_center_y, 
                                              ownship_target_x, ownship_target_y,
                                              fill="green", dash=(2,2), arrow=tk.LAST)
                
        except Exception as e:
            print(f"绘图错误: {str(e)}")
    
    def change_scale(self, direction):
        """改变比例尺"""
        if direction == "up" and self.current_scale_index < len(self.scale_options) - 1:
            self.current_scale_index += 1
        elif direction == "down" and self.current_scale_index > 0:
            self.current_scale_index -= 1
        
        self.draw_aircraft_positions()
    
    def update_input_fields(self):
        """根据计算模式更新显示的输入字段"""
        if self.calc_mode.get() == "mode1":
            self.mode2_frame.grid_forget()
            self.mode1_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E)
        else:
            self.mode1_frame.grid_forget()
            self.mode2_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E)
        self.calculate()
    
    def validate_input(self):
        """验证输入数据"""
        try:
            ownship_brg = float(self.ownship_brg.get()) if self.ownship_brg.get() else 0
            ownship_dist = float(self.ownship_dist.get()) if self.ownship_dist.get() else 0
            
            if not 0 <= ownship_brg <= 360:
                raise ValueError("本机方位必须在0-360度之间")
            if ownship_dist < 0:
                raise ValueError("本机距离不能为负数")
            
            if self.calc_mode.get() == "mode1":
                target_rel_brg = float(self.target_rel_brg.get()) if self.target_rel_brg.get() else 0
                target_rel_dist = float(self.target_rel_dist.get()) if self.target_rel_dist.get() else 0
                if not 0 <= target_rel_brg <= 360:
                    raise ValueError("敌机相对方位必须在0-360度之间")
                if target_rel_dist < 0:
                    raise ValueError("敌机距离不能为负数")
                return "mode1", ownship_brg, ownship_dist, target_rel_brg, target_rel_dist
            else:
                target_brg = float(self.target_brg.get()) if self.target_brg.get() else 0
                target_dist = float(self.target_dist.get()) if self.target_dist.get() else 0
                if not 0 <= target_brg <= 360:
                    raise ValueError("敌机靶眼方位必须在0-360度之间")
                if target_dist < 0:
                    raise ValueError("敌机距离不能为负数")
                return "mode2", ownship_brg, ownship_dist, target_brg, target_dist
                
        except ValueError as e:
            self.status_var.set(f"输入错误: {str(e)}")
            return None
        except:
            return None
    
    def calculate(self):
        """执行计算"""
        inputs = self.validate_input()
        if inputs is None:
            return
        
        mode, ownship_brg, ownship_dist, *rest = inputs
        
        try:
            ownship_x = ownship_dist * math.sin(math.radians(ownship_brg))
            ownship_y = ownship_dist * math.cos(math.radians(ownship_brg))
            
            if mode == "mode1":
                target_rel_brg, target_rel_dist = rest
                
                rel_x = target_rel_dist * math.sin(math.radians(target_rel_brg))
                rel_y = target_rel_dist * math.cos(math.radians(target_rel_brg))
                
                target_x = ownship_x + rel_x
                target_y = ownship_y + rel_y
                
                distance = math.sqrt(target_x**2 + target_y**2)
                angle_rad = math.atan2(target_x, target_y)
                angle_deg = math.degrees(angle_rad)
                if angle_deg < 0:
                    angle_deg += 360
                
                result = (f"敌机相对于靶眼的方位: {angle_deg:.1f}°\n"
                         f"敌机距离靶眼的距离: {distance:.1f}海里\n"
                         f"直角坐标(X,Y): ({target_x:.1f}, {target_y:.1f})")
                
                self.log_calculation(
                    "模式1",
                    f"本机: {ownship_brg}°/{ownship_dist}海里, 敌机相对: {target_rel_brg}°/{target_rel_dist}海里",
                    f"敌机靶眼: {angle_deg:.1f}°/{distance:.1f}海里"
                )
            else:
                target_brg, target_dist = rest
                
                target_x = target_dist * math.sin(math.radians(target_brg))
                target_y = target_dist * math.cos(math.radians(target_brg))
                
                rel_x = target_x - ownship_x
                rel_y = target_y - ownship_y
                
                distance = math.sqrt(rel_x**2 + rel_y**2)
                angle_rad = math.atan2(rel_x, rel_y)
                angle_deg = math.degrees(angle_rad)
                if angle_deg < 0:
                    angle_deg += 360
                
                result = (f"敌机相对本机方位: {angle_deg:.1f}°\n"
                         f"敌机距离本机距离: {distance:.1f}海里\n"
                         f"直角坐标(X,Y): ({rel_x:.1f}, {rel_y:.1f})")
                
                self.log_calculation(
                    "模式2",
                    f"本机: {ownship_brg}°/{ownship_dist}海里, 敌机靶眼: {target_brg}°/{target_dist}海里",
                    f"敌机相对: {angle_deg:.1f}°/{distance:.1f}海里"
                )
            
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            self.result_text.config(state=tk.DISABLED)
            self.status_var.set("计算完成")
            
            self.draw_aircraft_positions()
            
        except Exception as e:
            self.status_var.set(f"计算错误: {str(e)}")
            self.draw_aircraft_positions()
    
    def log_calculation(self, mode, inputs, results):
        """记录计算结果"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} | {mode} | {inputs} | {results}\n"
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            messagebox.showerror("日志错误", f"无法写入日志: {str(e)}")
    
    def clear_fields(self):
        """清空输入字段"""
        self.ownship_brg.set("")
        self.ownship_dist.set("")
        self.target_rel_brg.set("")
        self.target_rel_dist.set("")
        self.target_brg.set("")
        self.target_dist.set("")
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.status_var.set("已清空")
        
        self.draw_aircraft_positions()
    
    def view_log(self):
        """查看日志"""
        try:
            log_window = tk.Toplevel(self.root)
            log_window.title("计算日志")
            log_window.geometry("900x600")
            
            text_frame = ttk.Frame(log_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_area = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
            text_area.pack(fill=tk.BOTH, expand=True)
            
            with open(self.log_file, "r", encoding="utf-8") as f:
                text_area.insert(tk.END, f.read())
            
            text_area.config(state=tk.DISABLED)
            scrollbar.config(command=text_area.yview)
            
            close_btn = ttk.Button(log_window, text="关闭", command=log_window.destroy)
            close_btn.pack(pady=10)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取日志: {str(e)}")

def main():
    root = tk.Tk()
    app = RealTimeBullseyeCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
