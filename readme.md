  B.O.Y.O.U.N.G. Financial Suite

A double-entry financial accounting platform built completely in Python using a CustomTkinter GUI interface and an SQLite ledger tracking matrix. Enforces strict double-entry balancing across multiple corporate portfolios, complete with an interactive spreadsheet engine and automated reports.

* **Double-Entry Logger:** Enforces transaction symmetry by processing balanced split records.
* **Spreadsheet Engine:** Features a 15-row grid workspace with on-demand recalculation and persistence.
* **Transaction Journal:** Displays transaction histories utilizing a color-coded "traffic light grid".
* **Invoice Pagination Pipeline:** A 10-row viewport context tracking invoice pipelines ("Paid"/"Unpaid").
* **RAM Memory Cache Store:** Prevents repetitive disk reading queries to run efficiently on low-resource environments.


Installation
1. Python Requirement
Ensure you have **Python 3.8 to 3.11** installed on your system.

2. Install Required Packages
Open your terminal or command prompt and run the following command to install all the required libraries at once:

```bash
pip install customtkinter pandas

 How to Run & Project Architecture
Step 1: Open Terminal / Command Prompt
Launch your system's Command Prompt (Windows) or Terminal (Mac/Linux).

Step 2: Navigate to Your Project Directory
Use the cd command to enter the folder where your project files live:

DOS
cd path/to/your/project/folder
(For example, if your folder is named python inside your Desktop directory, you would type: cd Desktop/python)

Step 3: Run the Main Interface Script
Execute the main user interface file to launch the application:
python main_ui.py


 File Structure Directory Mapping
When navigating the project path folder, the script architecture maps to the following components:
├── main_ui.py          # Primary entry point (Initializes cache, UI loops, and window geometry)
├── database.py         # SQLite schema configurations, foreign key PRAGMAs, and initializations
├── engine.py           # Core transactional calculation logic and Pandas report generators
├── tab_entry.py        # Balanced general entry journal panel forms
├── tab_sheet.py        # Live spreadsheet calculation grid row context
├── tab_ledger.py       # Scrolling ledger timeline viewer
├── tab_invoices.py     # Paginated invoice workspace pipelines
├── tab_reports.py      # Monospaced monocolor dashboard statements
└── tab_settings.py     # Profile generation tools and database wiping tools
