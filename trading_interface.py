import tkinter as tk
from tkinter import ttk
import queue
import threading
import time
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
import nest_asyncio
from trading_bot import ForexTradingBot, calculate_rsi

# Import matplotlib for charting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Enable nested event loops
nest_asyncio.apply()

class ModernTradingInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Gold Trading Bot")
        self.root.geometry("900x700")
        
        # Set theme colors - Light theme
        self.bg_color = "#F5F5F5"  # Light gray background
        self.fg_color = "#333333"  # Dark gray text
        self.accent_color = "#2196F3"  # Blue accent
        self.success_color = "#4CAF50"  # Green for success
        self.warning_color = "#FFC107"  # Yellow for warnings
        self.danger_color = "#F44336"  # Red for errors
        self.panel_color = "#FFFFFF"  # White panels
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Create event loop for async operations
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Initialize trading bot
        self.bot = ForexTradingBot()
        
        # Initialize last market data for comparison
        self.last_market_data = None
        
        # Initialize trading parameters
        self.lot_size_var = tk.StringVar(value="0.01")
        self.sl_atr_var = tk.StringVar(value="1.5")
        self.tp_atr_var = tk.StringVar(value="3.0")
        self.max_positions_var = tk.StringVar(value="3")
        
        # Initialize log text
        self.log_text = tk.Text(height=5, width=80)
        
        # Configure styles
        self.configure_styles()

        # Initialize Matplotlib figure and axes for charting
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax1 = self.figure.add_subplot(111) # Primary axis for price/EMAs
        self.ax2 = None # Secondary axis for RSI, MACD later

        # Create chart canvas
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=self.root) # Parent to root initially

        # Create main container with padding
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create header with title and credits
        self.create_header()

        # Create main content area
        self.create_main_content()

        # Create footer with contact information
        self.create_footer()

        # Re-parent chart canvas to main_container after it's created
        self.chart_canvas.get_tk_widget().master = self.main_container

        # Start UI update thread
        self.update_thread = threading.Thread(target=self.update_ui, daemon=True)
        self.update_thread.start()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)

    def create_header(self):
        """Create header with title and credits"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="KODE Gold Trading Bot",
            font=("Segoe UI", 20, "bold"),
            foreground=self.accent_color
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Credits
        credits_label = ttk.Label(
            header_frame,
            text="Developed by Hong Lyher",
            font=("Segoe UI", 9),
            foreground=self.fg_color
        )
        credits_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # Community Info
        community_label = ttk.Label(
            header_frame,
            text="Under community: KODE SAHAKOM",
            font=("Segoe UI", 9),
            foreground=self.fg_color
        )
        community_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 0))

    def create_main_content(self):
        """Create main content area with all trading components"""
        content_frame = ttk.Frame(self.main_container)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Account Information Section
        self.create_account_section(content_frame)
        
        # Trading Parameters Section
        self.create_parameters_section(content_frame)
        
        # Trading Controls Section
        self.create_controls_section(content_frame)
        
        # Market Data Section
        self.create_market_data_section(content_frame)
        
        # Signal Panel Section
        self.create_signal_panel(content_frame)
        
        # Chart Section
        self.create_chart_section(content_frame)
        
        # Log Section
        self.create_log_section(content_frame)
        
        # Configure grid weights for content_frame
        content_frame.columnconfigure(0, weight=1)
        # Distribute vertical space more evenly, giving more to chart and logs
        content_frame.rowconfigure(0, weight=0) # Account Info
        content_frame.rowconfigure(1, weight=0) # Parameters
        content_frame.rowconfigure(2, weight=0) # Controls
        content_frame.rowconfigure(3, weight=0) # Market Data
        content_frame.rowconfigure(4, weight=0) # Signal Panel
        content_frame.rowconfigure(5, weight=3) # Chart - Give more weight to the chart
        content_frame.rowconfigure(6, weight=2) # Log - Give more weight to the log

    def create_account_section(self, parent):
        """Create account information section with modern design"""
        account_frame = ttk.LabelFrame(
            parent,
            text="Account Information",
            padding="5",
            style="Modern.TLabelframe"
        )
        account_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # All account info in one row
        ttk.Label(
            account_frame,
            text="Balance:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, padx=(0, 5))
        self.balance_label = ttk.Label(
            account_frame,
            text="0.00",
            font=("Segoe UI", 10)
        )
        self.balance_label.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(
            account_frame,
            text="Equity:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=2, padx=(0, 5))
        self.equity_label = ttk.Label(
            account_frame,
            text="0.00",
            font=("Segoe UI", 10)
        )
        self.equity_label.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(
            account_frame,
            text="Profit:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=4, padx=(0, 5))
        self.profit_label = ttk.Label(
            account_frame,
            text="0.00",
            font=("Segoe UI", 10)
        )
        self.profit_label.grid(row=0, column=5)

    def create_parameters_section(self, parent):
        """Create trading parameters section with modern design"""
        params_frame = ttk.LabelFrame(
            parent,
            text="Trading Parameters",
            padding="5",
            style="Modern.TLabelframe"
        )
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # All parameters in one row
        # Lot Size
        ttk.Label(
            params_frame,
            text="Lot Size:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, padx=(0, 5))
        lot_size_combo = ttk.Combobox(
            params_frame,
            textvariable=self.lot_size_var,
            values=["0.01", "0.02", "0.03", "0.04", "0.05", "0.06", "0.07", "0.08", "0.09", "0.1", 
                   "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"],
            width=7,
            state="readonly",
            style="Modern.TCombobox"
        )
        lot_size_combo.grid(row=0, column=1, padx=(0, 20))
        lot_size_combo.set("0.01")
        
        # SL ATR
        ttk.Label(
            params_frame,
            text="SL (ATR ×):",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=2, padx=(0, 5))
        sl_atr_combo = ttk.Combobox(
            params_frame,
            textvariable=self.sl_atr_var,
            values=["1.0", "1.2", "1.5", "1.8", "2.0", "2.5", "3.0"],
            width=7,
            state="readonly",
            style="Modern.TCombobox"
        )
        sl_atr_combo.grid(row=0, column=3, padx=(0, 20))
        sl_atr_combo.set("1.5")
        
        # TP ATR
        ttk.Label(
            params_frame,
            text="TP (ATR ×):",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=4, padx=(0, 5))
        tp_atr_combo = ttk.Combobox(
            params_frame,
            textvariable=self.tp_atr_var,
            values=["2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0"],
            width=7,
            state="readonly",
            style="Modern.TCombobox"
        )
        tp_atr_combo.grid(row=0, column=5, padx=(0, 20))
        tp_atr_combo.set("3.0")
        
        # Max Positions
        ttk.Label(
            params_frame,
            text="Max Positions:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=6, padx=(0, 5))
        max_positions_combo = ttk.Combobox(
            params_frame,
            textvariable=self.max_positions_var,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            width=7,
            state="readonly",
            style="Modern.TCombobox"
        )
        max_positions_combo.grid(row=0, column=7)
        max_positions_combo.set("3")

    def create_controls_section(self, parent):
        """Create trading controls section with modern design"""
        controls_frame = ttk.LabelFrame(
            parent,
            text="Trading Controls",
            padding="5",
            style="Modern.TLabelframe"
        )
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Controls in one row
        self.auto_trading_var = tk.BooleanVar(value=False)
        self.auto_trading_button = ttk.Button(
            controls_frame,
            text="Start Auto Trading",
            command=self.toggle_auto_trading,
            style="Accent.TButton"
        )
        self.auto_trading_button.grid(row=0, column=0, padx=5)
        
        self.close_all_button = ttk.Button(
            controls_frame,
            text="Close All Positions",
            command=self.close_all_positions,
            style="Danger.TButton"
        )
        self.close_all_button.grid(row=0, column=1, padx=5)

    def create_market_data_section(self, parent):
        """Create market data section with modern design"""
        market_frame = ttk.LabelFrame(
            parent,
            text="Market Data",
            padding="5",
            style="Modern.TLabelframe"
        )
        market_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Create a frame to hold all market data
        data_frame = ttk.Frame(market_frame)
        data_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid columns
        for i in range(8):  # 8 columns for 8 pairs of label-value
            data_frame.columnconfigure(i, weight=1)
        
        # First row - Labels and Second row - Values
        # Price
        ttk.Label(
            data_frame,
            text="Price:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, padx=5, pady=2, sticky=tk.E)
        self.price_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.price_label.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        
        # EMA5
        ttk.Label(
            data_frame,
            text="EMA5:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=1, padx=5, pady=2, sticky=tk.E)
        self.ema20_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.ema20_label.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        # EMA10
        ttk.Label(
            data_frame,
            text="EMA10:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=2, padx=5, pady=2, sticky=tk.E)
        self.ema50_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.ema50_label.grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        
        # RSI
        ttk.Label(
            data_frame,
            text="RSI:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=3, padx=5, pady=2, sticky=tk.E)
        self.rsi_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.rsi_label.grid(row=1, column=3, padx=5, pady=2, sticky=tk.W)
        
        # MACD
        ttk.Label(
            data_frame,
            text="MACD:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=4, padx=5, pady=2, sticky=tk.E)
        self.macd_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.macd_label.grid(row=1, column=4, padx=5, pady=2, sticky=tk.W)
        
        # Signal
        ttk.Label(
            data_frame,
            text="Signal:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=5, padx=5, pady=2, sticky=tk.E)
        self.macd_signal_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.macd_signal_label.grid(row=1, column=5, padx=5, pady=2, sticky=tk.W)
        
        # ADX
        ttk.Label(
            data_frame,
            text="ADX:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=6, padx=5, pady=2, sticky=tk.E)
        self.adx_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.adx_label.grid(row=1, column=6, padx=5, pady=2, sticky=tk.W)
        
        # ATR
        ttk.Label(
            data_frame,
            text="ATR:",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=7, padx=5, pady=2, sticky=tk.E)
        self.atr_label = ttk.Label(data_frame, text="0.00", font=("Segoe UI", 10))
        self.atr_label.grid(row=1, column=7, padx=5, pady=2, sticky=tk.W)
        
        # Configure row weights for data_frame
        data_frame.rowconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)

    def create_signal_panel(self, parent):
        """Create the signal panel section"""
        signal_frame = ttk.LabelFrame(
            parent,
            text="Trading Signals Status",
            padding="5",
            style="Modern.TLabelframe"
        )
        signal_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Frame to hold signals in a grid
        signals_grid_frame = ttk.Frame(signal_frame)
        signals_grid_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure columns for the signal grid
        for i in range(4): # Adjust range based on the number of signal indicators
            signals_grid_frame.columnconfigure(i, weight=1)
            
        # Signal Labels (will be updated dynamically)
        self.ema_cross_label = ttk.Label(signals_grid_frame, text="EMA Cross: --", font=("Segoe UI", 10))
        self.ema_cross_label.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.rsi_status_label = ttk.Label(signals_grid_frame, text="RSI: --", font=("Segoe UI", 10))
        self.rsi_status_label.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        self.macd_cross_label = ttk.Label(signals_grid_frame, text="MACD Cross: --", font=("Segoe UI", 10))
        self.macd_cross_label.grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        
        self.quick_buy_signal_label = ttk.Label(signals_grid_frame, text="Quick Buy: --", font=("Segoe UI", 10))
        self.quick_buy_signal_label.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        
        self.quick_sell_signal_label = ttk.Label(signals_grid_frame, text="Quick Sell: --", font=("Segoe UI", 10))
        self.quick_sell_signal_label.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

    def create_chart_section(self, parent):
        """Create the chart panel section"""
        chart_frame = ttk.LabelFrame(
            parent,
            text="Trading Chart",
            padding="5",
            style="Modern.TLabelframe"
        )
        chart_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # Create canvas for matplotlib chart
        self.chart_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for chart_frame
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

    def create_log_section(self, parent):
        """Create log section with modern design"""
        log_frame = ttk.LabelFrame(
            parent,
            text="Trading Log",
            padding="5",
            style="Modern.TLabelframe"
        )
        log_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # Trading Actions Log
        actions_frame = ttk.Frame(log_frame)
        actions_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(
            actions_frame,
            text="Trading Actions",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky=tk.W)
        
        self.actions_log = tk.Text(
            actions_frame,
            height=6, # Increased height slightly for more actions
            width=80,
            bg=self.panel_color,
            fg=self.fg_color,
            font=("Consolas", 9)
        )
        actions_scrollbar = ttk.Scrollbar(
            actions_frame,
            orient=tk.VERTICAL,
            command=self.actions_log.yview
        )
        self.actions_log.configure(yscrollcommand=actions_scrollbar.set)
        
        self.actions_log.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        actions_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.rowconfigure(1, weight=1)

    def create_footer(self):
        """Create footer with contact information"""
        footer_frame = ttk.Frame(self.main_container)
        footer_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Contact Information
        contact_text = """
        Contact Information:
        Telegram: @lyheryt
        Facebook: Hong Lyher
        """
        
        contact_label = ttk.Label(
            footer_frame,
            text=contact_text,
            font=("Segoe UI", 9),
            foreground=self.fg_color,
            justify=tk.LEFT
        )
        contact_label.grid(row=0, column=0, sticky=tk.W)
        
        # Copyright
        copyright_label = ttk.Label(
            footer_frame,
            text="© 2024 Gold Trading Bot. All rights reserved.",
            font=("Segoe UI", 8),
            foreground=self.fg_color
        )
        copyright_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

    def configure_styles(self):
        """Configure custom styles for modern look"""
        style = ttk.Style()
        
        # Configure theme colors
        style.configure(".",
            background=self.bg_color,
            foreground=self.fg_color,
            fieldbackground=self.panel_color
        )
        
        # Configure LabelFrame
        style.configure("Modern.TLabelframe",
            background=self.panel_color,
            foreground=self.fg_color
        )
        style.configure("Modern.TLabelframe.Label",
            background=self.panel_color,
            foreground=self.fg_color,
            font=("Segoe UI", 10, "bold")
        )
        
        # Configure Combobox
        style.configure("Modern.TCombobox",
            background=self.panel_color,
            foreground=self.fg_color,
            fieldbackground=self.panel_color,
            arrowcolor=self.fg_color
        )
        
        # Configure Buttons
        style.configure("Accent.TButton",
            background=self.accent_color,
            foreground=self.fg_color,
            font=("Segoe UI", 10)
        )
        style.configure("Danger.TButton",
            background=self.danger_color,
            foreground=self.fg_color,
            font=("Segoe UI", 10)
        )

    def toggle_auto_trading(self):
        """Toggle auto trading on/off"""
        if not self.auto_trading_var.get():
            self.auto_trading_var.set(True)
            self.auto_trading_button.configure(text="Stop Auto Trading")
            self.log_action("Auto trading started")
            # Start auto trading in a separate thread
            threading.Thread(target=self.run_auto_trading, daemon=True).start()
        else:
            self.auto_trading_var.set(False)
            self.auto_trading_button.configure(text="Start Auto Trading")
            self.log_action("Auto trading stopped")

    def run_auto_trading(self):
        """Run auto trading logic"""
        while self.auto_trading_var.get():
            try:
                # Get market data
                market_data = self.bot.get_market_data()
                if market_data is not None:
                    # Calculate indicators with even shorter periods for faster response
                    market_data['EMA20'] = market_data['close'].ewm(span=5, adjust=False).mean()
                    market_data['EMA50'] = market_data['close'].ewm(span=10, adjust=False).mean()
                    market_data['RSI'] = calculate_rsi(market_data['close'], 5)
                    
                    # Calculate MACD with faster periods
                    exp1 = market_data['close'].ewm(span=5, adjust=False).mean()
                    exp2 = market_data['close'].ewm(span=10, adjust=False).mean()
                    market_data['MACD'] = exp1 - exp2
                    market_data['MACD_Signal'] = market_data['MACD'].ewm(span=3, adjust=False).mean()
                    
                    # Calculate ATR
                    high_low = market_data['high'] - market_data['low']
                    high_close = abs(market_data['high'] - market_data['close'].shift())
                    low_close = abs(market_data['low'] - market_data['close'].shift())
                    ranges = pd.concat([high_low, high_close, low_close], axis=1)
                    true_range = ranges.max(axis=1)
                    market_data['ATR'] = true_range.rolling(5).mean()
                    
                    # Get the latest values
                    current_price = market_data['close'].iloc[-1]
                    ema20 = market_data['EMA20'].iloc[-1]
                    ema50 = market_data['EMA50'].iloc[-1]
                    rsi = market_data['RSI'].iloc[-1]
                    macd = market_data['MACD'].iloc[-1]
                    macd_signal = market_data['MACD_Signal'].iloc[-1]
                    atr = market_data['ATR'].iloc[-1]
                    
                    # Update Market Data labels
                    self.price_label.configure(text=f"{current_price:.2f}")
                    self.ema20_label.configure(text=f"{ema20:.2f}")
                    self.ema50_label.configure(text=f"{ema50:.2f}")
                    self.rsi_label.configure(text=f"{rsi:.2f}")
                    self.macd_label.configure(text=f"{macd:.2f}")
                    self.macd_signal_label.configure(text=f"{macd_signal:.2f}")
                    self.atr_label.configure(text=f"{atr:.2f}")
                    
                    # Evaluate Signal Conditions
                    ema_crossed_up = ema20 > ema50
                    ema_crossed_down = ema20 < ema50
                    macd_crossed_up = macd > macd_signal
                    macd_crossed_down = macd < macd_signal
                    rsi_overbought = rsi > 70
                    rsi_oversold = rsi < 30
                    
                    # Update Signal Panel Labels
                    if ema_crossed_up:
                        self.ema_cross_label.configure(text="EMA Cross: Up", foreground="green")
                    elif ema_crossed_down:
                        self.ema_cross_label.configure(text="EMA Cross: Down", foreground="red")
                    else:
                        self.ema_cross_label.configure(text="EMA Cross: --", foreground="black")
                        
                    if rsi_overbought:
                        self.rsi_status_label.configure(text=f"RSI: {rsi:.2f} (Overbought)", foreground="red")
                    elif rsi_oversold:
                         self.rsi_status_label.configure(text=f"RSI: {rsi:.2f} (Oversold)", foreground="green")
                    else:
                        self.rsi_status_label.configure(text=f"RSI: {rsi:.2f}", foreground="black")
                        
                    if macd_crossed_up:
                         self.macd_cross_label.configure(text="MACD Cross: Up", foreground="green")
                    elif macd_crossed_down:
                         self.macd_cross_label.configure(text="MACD Cross: Down", foreground="red")
                    else:
                         self.macd_cross_label.configure(text="MACD Cross: --", foreground="black")
                         
                    # Update Quick Signal Labels
                    quick_buy = (
                        (rsi < 80 and macd > macd_signal) or
                        (ema20 > ema50 and rsi < 85) or
                        (rsi < 30)
                    )
                    quick_sell = (
                        (rsi > 20 and macd < macd_signal) or
                        (ema20 < ema50 and rsi > 15) or
                        (rsi > 70)
                    )
                    
                    if quick_buy:
                        self.quick_buy_signal_label.configure(text="Quick Buy: ✓", foreground="green")
                    else:
                        self.quick_buy_signal_label.configure(text="Quick Buy: ✗", foreground="black")
                        
                    if quick_sell:
                        self.quick_sell_signal_label.configure(text="Quick Sell: ✓", foreground="red")
                    else:
                        self.quick_sell_signal_label.configure(text="Quick Sell: ✗", foreground="black")
                        
                    # --- Charting Logic --- 
                    # In a real-time scenario, you would update the chart data here
                    # and redraw the chart. This is a placeholder.
                    
                    # Fetch more historical data if needed for charting
                    # market_data = self.bot.get_market_data(num_candles=200) # Example: fetch 200 candles
                    
                    # Update chart data (e.g., append new candle data)
                    # self.ax1.clear() # Clear previous plot
                    # self.ax1.plot(market_data['time'], market_data['close']) # Example plot
                    # self.chart_canvas.draw_idle() # Redraw the canvas
                    
                    # Note: Real-time updating requires careful handling to avoid blocking the UI.
                    # Consider using Tkinter's root.after() to schedule chart updates.
                    
                    # --- End Charting Logic ---
                        
                    # Get trading parameters
                    volume = float(self.lot_size_var.get())
                    sl_atr = float(self.sl_atr_var.get())
                    tp_atr = float(self.tp_atr_var.get())
                    max_positions = int(self.max_positions_var.get())
                    
                    # Get current positions
                    positions = self.bot.get_open_positions()
                    buy_positions = []
                    sell_positions = []
                    
                    if positions:
                        for pos in positions:
                            if pos.symbol == self.bot.symbol:
                                if pos.type == mt5.ORDER_TYPE_BUY:
                                    buy_positions.append(pos)
                                else:
                                    sell_positions.append(pos)
                                    
                    # Check total number of open positions
                    total_open_positions = len(buy_positions) + len(sell_positions)
                    
                    # Buy conditions - More aggressive
                    # Only buy if total positions is less than max and there are no open sell positions
                    if total_open_positions < max_positions and len(sell_positions) == 0:
                        # Quick buy signals
                        quick_buy = (
                            (rsi < 80 and macd > macd_signal) or
                            (ema20 > ema50 and rsi < 85) or
                            (rsi < 30)
                        )
                        
                        # Simplified condition check for logging
                        buy_conditions_met = []
                        if (rsi < 80 and macd > macd_signal): buy_conditions_met.append("RSI<80 & MACD_Cross")
                        if (ema20 > ema50 and rsi < 85): buy_conditions_met.append("EMA_Cross & RSI<85")
                        if (rsi < 30): buy_conditions_met.append("RSI<30")
                        
                        if buy_conditions_met:
                             self.log_action(f"Buy Conditions Met: {', '.join(buy_conditions_met)}")
                        
                        if quick_buy: # Use combined quick_buy condition for entry
                            sl = current_price - (atr * sl_atr)
                            tp = current_price + (atr * tp_atr)
                            
                            self.log_action("Attempting to place BUY order...")
                            result = self.loop.run_until_complete(self._place_order_async(
                                mt5.ORDER_TYPE_BUY,
                                volume,
                                current_price,
                                sl,
                                tp
                            ))
                    
                    # Sell conditions - More aggressive
                    # Only sell if total positions is less than max and there are no open buy positions
                    if total_open_positions < max_positions and len(buy_positions) == 0:
                        # Quick sell signals
                        quick_sell = (
                            (rsi > 20 and macd < macd_signal) or
                            (ema20 < ema50 and rsi > 15) or
                            (rsi > 70)
                        )
                        
                        # Simplified condition check for logging
                        sell_conditions_met = []
                        if (rsi > 20 and macd < macd_signal): sell_conditions_met.append("RSI>20 & MACD_Cross")
                        if (ema20 < ema50 and rsi > 15): sell_conditions_met.append("EMA_Cross & RSI>15")
                        if (rsi > 70): sell_conditions_met.append("RSI>70")

                        if sell_conditions_met:
                             self.log_action(f"Sell Conditions Met: {', '.join(sell_conditions_met)}")

                        if quick_sell: # Use combined quick_sell condition for entry
                            sl = current_price + (atr * sl_atr)
                            tp = current_price - (atr * tp_atr)
                            
                            self.log_action("Attempting to place SELL order...")
                            result = self.loop.run_until_complete(self._place_order_async(
                                mt5.ORDER_TYPE_SELL,
                                volume,
                                current_price,
                                sl,
                                tp
                            ))
                    
                    # Check for exit conditions - More responsive
                    # Note: TP/SL are handled by MT5 automatically based on order parameters
                    # This section can be used for other exit strategies if needed, but currently TP/SL are set on order placement.
                    # We can log when a position is closed by checking open positions and comparing to previous state, but that adds complexity.
                    # For now, relying on MT5 for TP/SL closure and the bot's notification system.
                    
                    time.sleep(0.02) # Sleep for a short duration
                    
            except Exception as e:
                self.log_action(f"Error in trading loop: {str(e)}")
                time.sleep(1) # Short error recovery time

    async def _place_order_async(self, order_type, volume, price, sl, tp):
        """Async wrapper for placing orders"""
        result = self.bot.place_order(order_type, volume, price, sl, tp)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            action = "BUY" if order_type == mt5.ORDER_TYPE_BUY else "SELL"
            self.log_action(f"Placed {action} order: Volume={volume}, Price={price:.5f}, SL={sl:.5f}, TP={tp:.5f}") # Log detailed info
        elif result:
             self.log_action(f"Order placement failed: {result.comment} (retcode: {result.retcode})")
        else:
             self.log_action("Order placement failed: No result")
        return result

    async def _close_position_async(self, position_id, close_reason="Manual", profit=None):
        """Async wrapper for closing positions with reason and profit/loss logging"""
        # Get position info before closing to log details
        position = mt5.positions_get(ticket=position_id)
        if position:
            pos_type = "BUY" if position[0].type == mt5.ORDER_TYPE_BUY else "SELL"
            volume = position[0].volume
            entry_price = position[0].price_open
            current_price = mt5.symbol_info_tick(position[0].symbol).bid if pos_type == "BUY" else mt5.symbol_info_tick(position[0].symbol).ask
            current_profit = position[0].profit
            symbol = position[0].symbol
            
            self.log_action(f"Attempting to close {pos_type} position {position_id} for {symbol} (Volume={volume}, Entry={entry_price:.5f}, Current Profit={current_profit:.2f})")
            
            result = self.bot.close_position(position_id)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                # We might not get the final profit from the result, rely on position info before close or check account balance change
                # For simplicity, let's log the profit just before closing attempt
                self.log_action(f"Closed {pos_type} position {position_id}. Profit/Loss: {current_profit:.2f}") # Log profit/loss
            elif result:
                 self.log_action(f"Failed to close position {position_id}: {result.comment} (retcode: {result.retcode})")
            else:
                 self.log_action(f"Failed to close position {position_id}: No result")
            return result
        else:
            self.log_action(f"Position {position_id} not found for closing.")
            return None

    def close_all_positions(self):
        """Close all open positions"""
        positions = self.bot.get_open_positions()
        if positions:
            self.log_action("Attempting to close all positions...")
            for position in positions:
                if position.symbol == self.bot.symbol:
                    # Call the updated async close position method without specific reason/profit yet
                    # The detailed logging will happen inside _close_position_async
                    self.loop.run_until_complete(self._close_position_async(position.ticket))
            self.log_action("Finished attempting to close all positions.")
        else:
            self.log_action("No positions to close.")

    def update_ui(self):
        """Update UI elements with latest data"""
        while True:
            try:
                # Update account information
                account_info = self.bot.get_account_info()
                if account_info:
                    self.balance_label.configure(text=f"{account_info.balance:.2f}")
                    self.equity_label.configure(text=f"{account_info.equity:.2f}")
                    self.profit_label.configure(text=f"{account_info.profit:.2f}")
                
                # Market data updates are now handled in run_auto_trading
                # This update_ui focuses on account info and other potential future UI updates
                
                time.sleep(1)  # Update account info every second
                
            except Exception as e:
                self.log_action(f"Error updating UI: {str(e)}")
                time.sleep(1)

    def log_action(self, message):
        """Add trading action message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.actions_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.actions_log.see(tk.END)
        # Keep only last 200 lines (increased from 100 for more actions)
        if int(self.actions_log.index('end-1c').split('.')[0]) > 200:
            self.actions_log.delete('1.0', '2.0')

    def on_closing(self):
        """Handle window closing"""
        if self.auto_trading_var.get():
            self.auto_trading_var.set(False)
        self.bot.shutdown()
        self.loop.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernTradingInterface(root)
    root.mainloop() 