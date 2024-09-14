import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import re

class FamilyTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Family Tree App")

        # Initialize database
        self.conn = sqlite3.connect('family_tree.db')
        self.cursor = self.conn.cursor()
        self.setup_database()

        # Set up GUI components
        self.create_widgets()

    def setup_database(self):
        # Create table for members
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                gender TEXT,
                birth_date TEXT,
                mother_id INTEGER,
                father_id INTEGER,
                FOREIGN KEY(mother_id) REFERENCES members(id),
                FOREIGN KEY(father_id) REFERENCES members(id)
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        # Tabs
        self.tab_control = ttk.Notebook(self.root)

        # Tab1: Add Member
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='Add Member')
        self.create_add_member_tab()

        # Tab2: View Family Tree
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab2, text='View Family Tree')
        self.create_view_tree_tab()

        # Tab3: Visualize Family Tree
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab3, text='Visualize Family Tree')
        self.create_visualize_tab()

        self.tab_control.pack(expand=1, fill='both')

    def create_add_member_tab(self):
        # First Name
        ttk.Label(self.tab1, text="First Name:").grid(column=0, row=0, padx=10, pady=5, sticky='W')
        self.first_name_entry = ttk.Entry(self.tab1, width=30)
        self.first_name_entry.grid(column=1, row=0, padx=10, pady=5)

        # Last Name
        ttk.Label(self.tab1, text="Last Name:").grid(column=0, row=1, padx=10, pady=5, sticky='W')
        self.last_name_entry = ttk.Entry(self.tab1, width=30)
        self.last_name_entry.grid(column=1, row=1, padx=10, pady=5)

        # Gender
        ttk.Label(self.tab1, text="Gender:").grid(column=0, row=2, padx=10, pady=5, sticky='W')
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(self.tab1, textvariable=self.gender_var, values=["Male", "Female", "Other"])
        self.gender_combo.grid(column=1, row=2, padx=10, pady=5)

        # Birth Date
        ttk.Label(self.tab1, text="Birth Date (YYYY-MM-DD):").grid(column=0, row=3, padx=10, pady=5, sticky='W')
        self.birth_date_entry = ttk.Entry(self.tab1, width=30)
        self.birth_date_entry.grid(column=1, row=3, padx=10, pady=5)

        # Mother's Full Name
        ttk.Label(self.tab1, text="Mother's Full Name:").grid(column=0, row=4, padx=10, pady=5, sticky='W')
        self.mother_name_entry = ttk.Entry(self.tab1, width=30)
        self.mother_name_entry.grid(column=1, row=4, padx=10, pady=5)

        # Father's Full Name
        ttk.Label(self.tab1, text="Father's Full Name:").grid(column=0, row=5, padx=10, pady=5, sticky='W')
        self.father_name_entry = ttk.Entry(self.tab1, width=30)
        self.father_name_entry.grid(column=1, row=5, padx=10, pady=5)

        # Add Member Button
        self.add_member_button = ttk.Button(self.tab1, text="Add Member", command=self.add_member)
        self.add_member_button.grid(column=1, row=6, padx=10, pady=10, sticky='E')

    def create_view_tree_tab(self):
        self.tree_text = tk.Text(self.tab2, wrap='none')
        self.tree_text.pack(expand=1, fill='both')

        # Refresh Button
        self.refresh_button = ttk.Button(self.tab2, text="Refresh Tree", command=self.display_tree)
        self.refresh_button.pack(pady=10)

    def create_visualize_tab(self):
        # Visualize Button
        self.visualize_button = ttk.Button(self.tab3, text="Visualize Family Tree", command=self.visualize_tree)
        self.visualize_button.pack(pady=20)

        # Instructions
        ttk.Label(self.tab3, text="The family tree will be generated and opened as a PDF file.").pack()

    def add_member(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        if not first_name or not last_name:
            messagebox.showerror("Error", "First name and last name cannot be empty.")
            return

        gender = self.gender_var.get().strip() or None
        birth_date = self.validate_date(self.birth_date_entry.get().strip())

        mother_full_name = self.mother_name_entry.get().strip() or None
        father_full_name = self.father_name_entry.get().strip() or None

        mother_id = self._get_member_id_by_full_name(mother_full_name) if mother_full_name else None
        father_id = self._get_member_id_by_full_name(father_full_name) if father_full_name else None

        # Check for circular relationships
        new_member_id = self._get_next_member_id()
        if mother_id and self._check_circular_relationship(mother_id, new_member_id):
            messagebox.showerror("Error", "Adding this mother would create a circular relationship.")
            return
        if father_id and self._check_circular_relationship(father_id, new_member_id):
            messagebox.showerror("Error", "Adding this father would create a circular relationship.")
            return

        try:
            self.cursor.execute('''
                INSERT INTO members (first_name, last_name, gender, birth_date, mother_id, father_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, gender, birth_date, mother_id, father_id))
            self.conn.commit()
            messagebox.showinfo("Success", f"Added member: {first_name} {last_name}")
            self.clear_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Member '{first_name} {last_name}' already exists.")

    def clear_entries(self):
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.gender_var.set('')
        self.birth_date_entry.delete(0, tk.END)
        self.mother_name_entry.delete(0, tk.END)
        self.father_name_entry.delete(0, tk.END)

    def validate_date(self, date_text):
        if not date_text:
            return None
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_text):
            return date_text
        else:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return None

    def _get_member_id_by_full_name(self, full_name):
        names = full_name.strip().split()
        if len(names) < 2:
            messagebox.showerror("Error", f"Full name '{full_name}' must include both first and last names.")
            return None
        first_name = names[0]
        last_name = ' '.join(names[1:])
        self.cursor.execute('''
            SELECT id FROM members WHERE first_name = ? AND last_name = ?
        ''', (first_name, last_name))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            messagebox.showerror("Error", f"Member '{full_name}' not found.")
            return None

    def _get_next_member_id(self):
        self.cursor.execute('SELECT seq FROM sqlite_sequence WHERE name="members"')
        result = self.cursor.fetchone()
        return (result[0] + 1) if result else 1

    def _check_circular_relationship(self, start_id, target_id):
        # Prevent circular relationships
        to_visit = [start_id]
        visited = set()
        while to_visit:
            current_id = to_visit.pop()
            if current_id == target_id:
                return True
            visited.add(current_id)
            self.cursor.execute('''
                SELECT id FROM members
                WHERE mother_id = ? OR father_id = ?
            ''', (current_id, current_id))
            children = [row[0] for row in self.cursor.fetchall()]
            to_visit.extend(child for child in children if child not in visited)
        return False

    def display_tree(self):
        self.tree_text.delete(1.0, tk.END)
        roots = self.get_roots()
        visited = set()
        for root_id, first_name, last_name in roots:
            full_name = f"{first_name} {last_name}"
            self.display_tree_recursive(root_id, full_name, 0, visited)

    def get_roots(self):
        # Find all root members (members without parents)
        self.cursor.execute('''
            SELECT id, first_name, last_name FROM members
            WHERE mother_id IS NULL AND father_id IS NULL
        ''')
        return self.cursor.fetchall()

    def display_tree_recursive(self, person_id, full_name, level, visited):
        if person_id in visited:
            return
        visited.add(person_id)
        self.tree_text.insert(tk.END, '    ' * level + f"- {full_name}\n")
        # Get children of the current person
        self.cursor.execute('''
            SELECT id, first_name, last_name FROM members
            WHERE mother_id = ? OR father_id = ?
        ''', (person_id, person_id))
        children = self.cursor.fetchall()
        for child_id, first_name, last_name in children:
            child_full_name = f"{first_name} {last_name}"
            self.display_tree_recursive(child_id, child_full_name, level + 1, visited)

    def visualize_tree(self):
        try:
            from graphviz import Digraph
        except ImportError:
            messagebox.showerror("Error", "Graphviz is not installed. Please install it to use this feature.")
            return

        dot = Digraph(comment='Family Tree')

        # Add nodes for each member with attributes
        self.cursor.execute('SELECT id, first_name, last_name, gender, birth_date FROM members')
        members = self.cursor.fetchall()
        for member_id, first_name, last_name, gender, birth_date in members:
            label = f"{first_name} {last_name}"
            if birth_date:
                label += f"\nBorn: {birth_date}"
            shape = 'ellipse'
            color = 'black'
            if gender:
                if gender.lower() == 'male':
                    shape = 'box'
                    color = 'blue'
                elif gender.lower() == 'female':
                    shape = 'oval'
                    color = 'red'
            dot.node(str(member_id), label, shape=shape, color=color)

        # Add edges for relationships
        self.cursor.execute('SELECT id, mother_id, father_id FROM members')
        relationships = self.cursor.fetchall()
        for child_id, mother_id, father_id in relationships:
            if mother_id:
                dot.edge(str(mother_id), str(child_id), label='mother', color='red')
            if father_id:
                dot.edge(str(father_id), str(child_id), label='father', color='blue')

        dot.render('family_tree.gv', view=True)
        messagebox.showinfo("Success", "Family tree visualized. Check the 'family_tree.gv.pdf' file.")

    def on_closing(self):
        self.conn.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FamilyTreeApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
