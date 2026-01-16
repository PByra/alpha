import sys
import threading
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QTabWidget, QListWidget, QListWidgetItem, QProgressBar, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QMetaType
from PyQt5.QtGui import QFont, QColor

# Try to import the scraper, handle gracefully if dependencies missing
try:
    from src.scraper import StockDataScraper
    SCRAPER_AVAILABLE = True
except ImportError as e:
    SCRAPER_AVAILABLE = False
    IMPORT_ERROR = str(e)


class WorkerSignals(QObject):
    """Signals for threaded operations"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(str)


class Worker(QThread):
    """Worker thread for running tasks without blocking UI"""
    def __init__(self, task_func, *args):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            result = self.task_func(*self.args)
            self.signals.result.emit(str(result))
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
            self.signals.finished.emit()


class CommandCenter(QMainWindow):
    """Main dashboard command center for Alpha application"""
    
    def __init__(self):
        super().__init__()
        self.scraper = None
        self.worker = None
        
        # Initialize scraper if available
        if SCRAPER_AVAILABLE:
            try:
                self.scraper = StockDataScraper()
            except Exception as e:
                print(f"Warning: Could not initialize scraper: {e}")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Alpha - Command Center")
        self.setGeometry(100, 100, 1000, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = self.create_left_panel()
        
        # Right panel - Tabs (Status, Logs, Results)
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("ALPHA\nCommand Center")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Data Collection Section
        section_label = QLabel("📊 Data Collection")
        section_font = QFont()
        section_font.setPointSize(12)
        section_font.setBold(True)
        section_label.setFont(section_font)
        layout.addWidget(section_label)
        
        # Scraper buttons
        fetch_tickers_btn = QPushButton("Fetch S&P 500 Tickers")
        fetch_tickers_btn.clicked.connect(self.fetch_tickers)
        layout.addWidget(fetch_tickers_btn)
        
        fetch_us_tickers_btn = QPushButton("Fetch All US Tradable Tickers")
        fetch_us_tickers_btn.clicked.connect(self.fetch_us_tickers)
        layout.addWidget(fetch_us_tickers_btn)
        
        fetch_all_tickers_btn = QPushButton("Fetch ALL US Tickers (~12,000+)")
        fetch_all_tickers_btn.clicked.connect(self.fetch_all_tickers)
        layout.addWidget(fetch_all_tickers_btn)
        
        fetch_data_btn = QPushButton("Download S&P 500 Data (30yr)")
        fetch_data_btn.clicked.connect(self.fetch_stock_data)
        layout.addWidget(fetch_data_btn)
        
        fetch_us_data_btn = QPushButton("Download All US Data (30yr)")
        fetch_us_data_btn.clicked.connect(self.fetch_us_stock_data)
        layout.addWidget(fetch_us_data_btn)
        
        fetch_all_data_btn = QPushButton("Download ALL Stocks (30yr)")
        fetch_all_data_btn.clicked.connect(self.fetch_all_stock_data)
        layout.addWidget(fetch_all_data_btn)
        
        layout.addSpacing(15)
        
        # CSV Import Section
        csv_label = QLabel("📥 CSV Import")
        csv_label.setFont(section_font)
        layout.addWidget(csv_label)
        
        import_csv_btn = QPushButton("Import CSV File")
        import_csv_btn.clicked.connect(self.import_csv_file)
        layout.addWidget(import_csv_btn)
        
        import_csv_folder_btn = QPushButton("Import CSV Folder")
        import_csv_folder_btn.clicked.connect(self.import_csv_folder)
        layout.addWidget(import_csv_folder_btn)
        
        layout.addSpacing(15)
        
        # Analysis Section
        analysis_label = QLabel("🔬 Analysis")
        analysis_label.setFont(section_font)
        layout.addWidget(analysis_label)
        
        analyze_btn = QPushButton("Run Analysis")
        analyze_btn.setEnabled(False)  # Placeholder
        layout.addWidget(analyze_btn)
        
        model_btn = QPushButton("Train Model")
        model_btn.setEnabled(False)  # Placeholder
        layout.addWidget(model_btn)
        
        layout.addSpacing(15)
        
        # Dashboard Section
        dashboard_label = QLabel("📈 Dashboard")
        dashboard_label.setFont(section_font)
        layout.addWidget(dashboard_label)
        
        visualize_btn = QPushButton("View Dashboard")
        visualize_btn.setEnabled(False)  # Placeholder
        layout.addWidget(visualize_btn)
        
        layout.addSpacing(20)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Exit button
        layout.addStretch()
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        layout.addWidget(exit_btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Create the right panel with tabs"""
        tabs = QTabWidget()
        
        # Status Tab
        status_widget = QWidget()
        status_layout = QVBoxLayout()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        status_layout.addWidget(QLabel("System Status:"))
        status_layout.addWidget(self.status_text)
        status_widget.setLayout(status_layout)
        tabs.addTab(status_widget, "Status")
        
        # Log Tab
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(QLabel("Operation Logs:"))
        log_layout.addWidget(self.log_text)
        log_widget.setLayout(log_layout)
        tabs.addTab(log_widget, "Logs")
        
        # Results Tab
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        self.results_list = QListWidget()
        results_layout.addWidget(QLabel("Results:"))
        results_layout.addWidget(self.results_list)
        results_widget.setLayout(results_layout)
        tabs.addTab(results_widget, "Results")
        
        # Initialize status
        self.log("Alpha Command Center initialized")
        self.update_status()
        
        return tabs
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def update_status(self):
        """Update the status display"""
        scraper_status = "🟢 Available" if SCRAPER_AVAILABLE and self.scraper else "🔴 Missing dependencies"
        data_dirs = ""
        if self.scraper:
            data_dirs = f"""
📁 Data Directories:
   Raw: {self.scraper.raw_dir}
   Processed: {self.scraper.processed_dir}"""
        
        status = f"""
🟢 System Status: Ready

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 Scraper: {scraper_status}{data_dirs}

🔄 Pipeline Status:
   [✓] Dashboard initialized
   [ ] Data collection
   [ ] Analysis pending
   [ ] Model training pending
   [ ] Results visualization pending
        """
        self.status_text.setText(status)
    
    def fetch_tickers(self):
        """Fetch S&P 500 tickers in background thread"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", f"Scraper not available. Please install dependencies:\npip install -r requirements.txt\n\nError: {IMPORT_ERROR if not SCRAPER_AVAILABLE else 'Scraper init failed'}")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        self.log("Starting S&P 500 ticker fetch...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        
        self.worker = Worker(self.scraper.get_sp500_tickers)
        self.worker.signals.result.connect(self.on_fetch_tickers_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def fetch_us_tickers(self):
        """Fetch all US tradable tickers in background thread"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", f"Scraper not available. Please install dependencies:\npip install -r requirements.txt\n\nError: {IMPORT_ERROR if not SCRAPER_AVAILABLE else 'Scraper init failed'}")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        self.log("Starting US tradable ticker fetch...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        
        self.worker = Worker(self.scraper.get_us_tradable_tickers)
        self.worker.signals.result.connect(self.on_fetch_us_tickers_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def fetch_all_tickers(self):
        """Fetch ALL US tickers (~12,000+) in background thread"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", f"Scraper not available. Please install dependencies:\npip install -r requirements.txt\n\nError: {IMPORT_ERROR if not SCRAPER_AVAILABLE else 'Scraper init failed'}")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        self.log("Starting comprehensive US ticker fetch (~12,000+ tickers)...")
        self.log("⏳ Fetching from: SEC EDGAR, NASDAQ, NYSE, Russell Indices, OTC Markets...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        
        self.worker = Worker(self.scraper.get_all_us_tickers)
        self.worker.signals.result.connect(self.on_fetch_all_tickers_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def fetch_stock_data(self):
        """Fetch 30 years of S&P 500 stock data in background thread"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", f"Scraper not available. Please install dependencies:\npip install -r requirements.txt\n\nError: {IMPORT_ERROR if not SCRAPER_AVAILABLE else 'Scraper init failed'}")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        self.log("Starting 30-year S&P 500 stock data download...")
        self.log("⏳ This will take approximately 12-15 minutes. Processing ~500 companies...")
        self.log("⚠️  Using smart rate limiting to avoid being blocked")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        
        def download_data():
            return self.scraper.download_sp500_30years(delay=1.5)
        
        self.worker = Worker(download_data)
        self.worker.signals.result.connect(self.on_stock_data_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def fetch_us_stock_data(self):
        """Fetch 30 years of all US tradable stock data in background thread"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", f"Scraper not available. Please install dependencies:\npip install -r requirements.txt\n\nError: {IMPORT_ERROR if not SCRAPER_AVAILABLE else 'Scraper init failed'}")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        self.log("Starting 30-year US tradable stock data download...")
        self.log("⏳ This will take longer due to the larger number of stocks...")
        self.log("⚠️  Using smart rate limiting to avoid being blocked")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        
        def download_data():
            return self.scraper.download_us_tradable_30years(delay=1.5)
        
        self.worker = Worker(download_data)
        self.worker.signals.result.connect(self.on_stock_data_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def fetch_all_stock_data(self):
        """Fetch 30 years of ALL US stock data (~12,000+) in background thread"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", f"Scraper not available. Please install dependencies:\npip install -r requirements.txt\n\nError: {IMPORT_ERROR if not SCRAPER_AVAILABLE else 'Scraper init failed'}")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        self.log("⚠️  WARNING: Starting comprehensive 30-year download for ~12,000+ stocks!")
        self.log("⏳ This will take 5-8+ hours depending on rate limits and network...")
        self.log("📊 Processing from all US exchanges: NYSE, NASDAQ, Russell, OTC, etc.")
        self.log("⚠️  Do NOT close this window. Progress will be logged here.")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        
        def download_data():
            return self.scraper.download_all_us_30years(delay=1.5)
        
        self.worker = Worker(download_data)
        self.worker.signals.result.connect(self.on_stock_data_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def on_fetch_tickers_complete(self, result):
        """Handle S&P 500 ticker fetch completion"""
        self.log(f"✓ S&P 500 ticker fetch complete: {result}")
        self.results_list.addItem(QListWidgetItem(f"S&P 500 tickers fetched at {datetime.now().strftime('%H:%M:%S')}"))
        self.update_status()
    
    def on_fetch_us_tickers_complete(self, result):
        """Handle US tradable ticker fetch completion"""
        self.log(f"✓ US tradable ticker fetch complete: {result}")
        self.results_list.addItem(QListWidgetItem(f"US tradable tickers fetched at {datetime.now().strftime('%H:%M:%S')}"))
        self.update_status()
    
    def on_fetch_all_tickers_complete(self, result):
        """Handle all US ticker fetch completion"""
        try:
            if isinstance(result, str):
                import ast
                result_list = ast.literal_eval(result) if result.startswith('[') else None
                count = len(result_list) if result_list else 0
            else:
                count = len(result) if isinstance(result, (list, set)) else 0
            
            self.log(f"✓ ALL US ticker fetch complete: {count} tickers")
            self.results_list.addItem(QListWidgetItem(f"All US tickers fetched ({count}) at {datetime.now().strftime('%H:%M:%S')}"))
        except:
            self.log(f"✓ All US ticker fetch complete")
            self.results_list.addItem(QListWidgetItem(f"All US tickers fetched at {datetime.now().strftime('%H:%M:%S')}"))
        self.update_status()
    
    def on_stock_data_complete(self, result):
        """Handle stock data download completion"""
        try:
            # Parse result if it's a string representation of dict
            if isinstance(result, str):
                import ast
                result_dict = ast.literal_eval(result) if result.startswith('{') else None
            else:
                result_dict = result
            
            if result_dict and isinstance(result_dict, dict):
                success = result_dict.get('success_count', 0)
                total = result_dict.get('total_tickers', 0)
                self.log(f"✓ Stock data download complete: {success}/{total} successful")
                self.results_list.addItem(QListWidgetItem(f"Downloaded 30-year data for {success} stocks at {datetime.now().strftime('%H:%M:%S')}"))
            else:
                self.log(f"✓ Stock data download completed: {result}")
                self.results_list.addItem(QListWidgetItem(f"Data download completed at {datetime.now().strftime('%H:%M:%S')}"))
        except:
            self.log(f"✓ Stock data download process completed")
            self.results_list.addItem(QListWidgetItem(f"Data download completed at {datetime.now().strftime('%H:%M:%S')}"))
    
    def import_csv_file(self):
        """Import a single CSV file and convert to JSON"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", "Scraper not available. Please install dependencies:\npip install -r requirements.txt")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        self.log(f"Starting CSV import: {file_path}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        
        def convert_csv():
            return self.scraper.convert_csv_to_json(file_path)
        
        self.worker = Worker(convert_csv)
        self.worker.signals.result.connect(self.on_csv_import_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def import_csv_folder(self):
        """Import all CSV files from a folder and convert to JSON"""
        if not SCRAPER_AVAILABLE or self.scraper is None:
            QMessageBox.warning(self, "Error", "Scraper not available. Please install dependencies:\npip install -r requirements.txt")
            self.log("❌ Scraper unavailable - install dependencies")
            return
        
        # Open folder dialog
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with CSV Files",
            ""
        )
        
        if not folder_path:
            return
        
        self.log(f"Starting batch CSV import from: {folder_path}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)
        
        def convert_folder():
            return self.scraper.batch_convert_csv_folder(folder_path)
        
        self.worker = Worker(convert_folder)
        self.worker.signals.result.connect(self.on_csv_import_complete)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def on_csv_import_complete(self, result):
        """Handle CSV import completion"""
        try:
            # Parse result if it's a string representation of dict
            if isinstance(result, str):
                import ast
                result_dict = ast.literal_eval(result) if result.startswith('{') else None
            else:
                result_dict = result
            
            if result_dict and isinstance(result_dict, dict):
                success = result_dict.get('successful_tickers', 0)
                failed = result_dict.get('failed_tickers', 0)
                total = success + failed
                self.log(f"✓ CSV import complete: {success}/{total} tickers successfully converted to JSON")
                if failed > 0:
                    self.log(f"⚠️  {failed} tickers failed conversion")
                self.results_list.addItem(QListWidgetItem(f"CSV import: {success} tickers converted at {datetime.now().strftime('%H:%M:%S')}"))
            else:
                self.log(f"✓ CSV import completed: {result}")
                self.results_list.addItem(QListWidgetItem(f"CSV import completed at {datetime.now().strftime('%H:%M:%S')}"))
        except Exception as e:
            self.log(f"⚠️  Could not parse CSV import result: {str(e)}")
            self.results_list.addItem(QListWidgetItem(f"CSV import completed at {datetime.now().strftime('%H:%M:%S')}"))
    
    def on_task_error(self, error):
        """Handle task errors"""
        self.log(f"❌ Error: {error}")
        self.statusBar().showMessage(f"Error: {error}")
    
    def on_task_finished(self):
        """Handle task completion"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Task complete")


def main():
    """Launch the command center"""
    app = QApplication(sys.argv)
    
    # Register custom types for thread-safe signal passing
    try:
        from PyQt5.QtGui import QTextCursor
        QMetaType.registerMetaType(QTextCursor)
    except:
        pass
    
    # Set application style
    app.setStyle('Fusion')
    
    window = CommandCenter()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
