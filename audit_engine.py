import sqlite3
from datetime import datetime
from database import DATABASE_NAME

class AuditEngine:
    @staticmethod
    def run_system_audit(profile_id):
        errors = []
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT row_index, description, quantity, rate 
                FROM grid_items WHERE profile_id = ?
            """, (profile_id,))
            grid_items = cursor.fetchall()
            
            for item in grid_items:
                row_idx, desc, qty, rate = item
                

                if (qty != 0.0 or rate != 0.0) and (not desc or desc.strip() == ""):
                    errors.append({
                        "tab": "Interactive Sheet",
                        "type": "Blank Description",
                        "msg": f"Row {row_idx} has a total amount calculated but the item description is completely empty."
                    })
                

                if qty < 0 or rate < 0:
                    errors.append({
                        "tab": "Interactive Sheet",
                        "type": "Negative Number",
                        "msg": f"Row {row_idx} has a negative quantity or rate. Please use positive numbers."
                    })
        except sqlite3.OperationalError:
            pass


        try:
            cursor.execute("""
                SELECT invoice_id, customer_name, amount, due_date 
                FROM invoices WHERE profile_id = ?
            """, (profile_id,))
            invoices = cursor.fetchall()
            
            for inv in invoices:
                inv_id, name, amount, due_date = inv
                
                if not name or name.strip() == "":
                    errors.append({
                        "tab": "Track Invoices",
                        "type": "Missing Name",
                        "msg": f"Invoice #{inv_id} is missing the customer name."
                    })
                
                if amount < 0:
                    errors.append({
                        "tab": "Track Invoices",
                        "type": "Negative Amount",
                        "msg": f"Invoice #{inv_id} for '{name}' has a negative amount. Invoices cannot be less than zero."
                    })
        except sqlite3.OperationalError:
            pass

        conn.close()
        return errors
