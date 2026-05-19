import customtkinter as ctk

from core.analytics import calculate_health_score, get_consumer_profile


class ProfilePage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.db = app.db

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        # ---- Header ----
        ctk.CTkLabel(container, text="消费画像",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(
            anchor="w", padx=25, pady=(25, 20))

        # ---- Personality Card ----
        self.personality_card = ctk.CTkFrame(container, corner_radius=14)
        self.personality_card.pack(fill="x", padx=25, pady=(0, 15))

        self.emoji_label = ctk.CTkLabel(self.personality_card, text="",
                                        font=ctk.CTkFont(size=56))
        self.emoji_label.pack(pady=(22, 4))

        self.personality_title = ctk.CTkLabel(
            self.personality_card, text="",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.personality_title.pack()

        self.personality_desc = ctk.CTkLabel(
            self.personality_card, text="",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray60"),
            wraplength=700,
            justify="center",
        )
        self.personality_desc.pack(padx=30, pady=(6, 6))

        # savings rate bar under personality
        self.savings_bar_frame = ctk.CTkFrame(self.personality_card, fg_color="transparent")
        self.savings_bar_frame.pack(fill="x", padx=40, pady=(4, 18))

        self.savings_label = ctk.CTkLabel(
            self.savings_bar_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray55"),
        )
        self.savings_label.pack(anchor="w", pady=(0, 4))

        self.savings_bar_bg = ctk.CTkFrame(
            self.savings_bar_frame,
            fg_color=("gray90", "gray22"), height=18, corner_radius=9,
        )
        self.savings_bar_bg.pack(fill="x")
        self.savings_bar_fill = ctk.CTkFrame(
            self.savings_bar_bg, fg_color="#4CAF50", height=18, corner_radius=9,
        )
        self.savings_bar_fill.place(relx=0, rely=0, relheight=1, relwidth=0)

        # ---- Suggestion Card ----
        self.suggestion_card = ctk.CTkFrame(container, corner_radius=12)
        self.suggestion_card.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(self.suggestion_card, text="💡 个性化建议",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(16, 6))

        self.suggestion_text = ctk.CTkLabel(
            self.suggestion_card, text="",
            font=ctk.CTkFont(size=13),
            wraplength=700,
            justify="left",
        )
        self.suggestion_text.pack(anchor="w", padx=20, pady=(0, 16))

        # ---- Top Categories Card ----
        self.cat_card = ctk.CTkFrame(container, corner_radius=12)
        self.cat_card.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(self.cat_card, text="📂 本月支出 Top 5",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(16, 10))

        self.cat_list = ctk.CTkFrame(self.cat_card, fg_color="transparent")
        self.cat_list.pack(fill="x", padx=20, pady=(0, 16))

        # ---- Health Breakdown Card ----
        self.health_card = ctk.CTkFrame(container, corner_radius=12)
        self.health_card.pack(fill="x", padx=25, pady=(0, 25))

        ctk.CTkLabel(self.health_card, text="📊 财务健康评分详情",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(16, 4))

        self.health_total_label = ctk.CTkLabel(
            self.health_card, text="",
            font=ctk.CTkFont(size=36, weight="bold"),
        )
        self.health_total_label.pack(pady=(0, 4))

        self.health_breakdown = ctk.CTkFrame(self.health_card, fg_color="transparent")
        self.health_breakdown.pack(fill="x", padx=20, pady=(4, 16))

    # ==================================================================
    def on_show(self):
        self.refresh()

    def refresh(self):
        profile = get_consumer_profile(self.db)
        health = calculate_health_score(self.db)

        # --- Personality ---
        self.emoji_label.configure(text=profile["emoji"])
        self.personality_title.configure(text=profile["title"])
        self.personality_desc.configure(text=profile["desc"])

        # savings bar
        sr = profile["savings_rate"]
        self.savings_label.configure(
            text=f"本月储蓄率: {sr}%  "
            f"({'收入 > 支出' if profile['balance'] >= 0 else '支出 > 收入'})"
        )
        bar_pct = min(sr / 100, 1.0)
        self.savings_bar_fill.place(relx=0, rely=0, relheight=1, relwidth=max(bar_pct, 0.01))

        # --- Suggestion ---
        self.suggestion_text.configure(text=profile["suggestion"])

        # --- Top categories ---
        for w in self.cat_list.winfo_children():
            w.destroy()

        top = profile["top_categories"]
        if not top:
            ctk.CTkLabel(self.cat_list, text="暂无支出数据",
                         font=ctk.CTkFont(size=12),
                         text_color=("gray45", "gray55")).pack(pady=8)
        else:
            max_amt = top[0]["amount"] if top else 1
            cat_colors = [
                "#EF5350", "#FF7043", "#FFA726", "#42A5F5", "#7E57C2",
            ]
            for i, cat in enumerate(top):
                self._add_cat_bar(
                    cat["name"], cat["amount"], cat["pct"],
                    max_amt, cat_colors[i % len(cat_colors)],
                )

        # --- Health breakdown ---
        score = health["score"]
        color = health["color"]
        self.health_total_label.configure(
            text=f"{score} 分 · {health['label']}",
            text_color=color,
        )

        for w in self.health_breakdown.winfo_children():
            w.destroy()

        bd = health["breakdown"]
        dim_colors = {
            "savings": "#4CAF50",
            "coverage": "#2196F3",
            "consistency": "#FF9800",
            "diversity": "#7E57C2",
        }
        for key in ["savings", "coverage", "consistency", "diversity"]:
            item = bd[key]
            self._add_health_row(
                item["label"], item["score"], item["max"],
                dim_colors.get(key, "#888"),
            )

    def _add_cat_bar(self, name: str, amount: float, pct: float,
                     max_amt: float, color: str):
        row = ctk.CTkFrame(self.cat_list, fg_color="transparent")
        row.pack(fill="x", pady=4)

        ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=13),
                     width=70, anchor="w").pack(side="left")

        bar_bg = ctk.CTkFrame(row, fg_color=("gray90", "gray22"), height=20,
                              corner_radius=10)
        bar_bg.pack(side="left", fill="x", expand=True, padx=(8, 8))

        rel = max_amt / 1 if max_amt == 0 else max_amt
        bar_fill = ctk.CTkFrame(bar_bg, fg_color=color, height=20,
                                corner_radius=10)
        bar_fill.place(relx=0, rely=0, relheight=1,
                       relwidth=max(amount / rel, 0.02))

        ctk.CTkLabel(row, text=f"¥{amount:,.0f}  {pct}%",
                     font=ctk.CTkFont(size=12),
                     text_color=("gray40", "gray60"),
                     width=90).pack(side="left")

    def _add_health_row(self, label: str, score: int, max_val: int, color: str):
        row = ctk.CTkFrame(self.health_breakdown, fg_color="transparent")
        row.pack(fill="x", pady=5)

        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13, weight="bold"),
                     width=70, anchor="w").pack(side="left")

        bar_bg = ctk.CTkFrame(row, fg_color=("gray90", "gray22"), height=18,
                              corner_radius=9)
        bar_bg.pack(side="left", fill="x", expand=True, padx=(10, 10))

        pct = score / max_val if max_val > 0 else 0
        bar_fill = ctk.CTkFrame(bar_bg, fg_color=color, height=18,
                                corner_radius=9)
        bar_fill.place(relx=0, rely=0, relheight=1, relwidth=max(pct, 0.03))

        ctk.CTkLabel(row, text=f"{score} / {max_val}",
                     font=ctk.CTkFont(size=12),
                     text_color=("gray40", "gray60"),
                     width=44).pack(side="left")
