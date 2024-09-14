import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import askstring
import re

# Optional: For visualization
try:
    from graphviz import Digraph
    GRAPHVIZ_INSTALLED = True
except ImportError:
    GRAPHVIZ_INSTALLED = False

class Person:
    def __init__(self, name, person_id, gender=None, birth_date=None):
        self.id = person_id
        self.name = name
        self.gender = gender
        self.birth_date = birth_date

class FamilyTree:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        # Create table for members
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                gender TEXT,
                birth_date TEXT
            )
        ''')

        # Create table for relationships
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                parent_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL DEFAULT 'parent',
                FOREIGN KEY(parent_id) REFERENCES members(id),
                FOREIGN KEY(child_id) REFERENCES members(id),
                PRIMARY KEY (parent_id, child_id)
            )
        ''')

        self.conn.commit()

    def add_member(self, name, gender=None, birth_date=None):
        try:
            self.cursor.execute('INSERT INTO members (name, gender, birth_date) VALUES (?, ?, ?)',
                                (name, gender, birth_date))
            self.conn.commit()
            return True, f"Added member: {name}"
        except sqlite3.IntegrityError:
            return False, f"Member '{name}' already exists."

    def _get_member_id(self, name):
        self.cursor.execute('SELECT id FROM members WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_members(self):
        self.cursor.execute('SELECT name FROM members ORDER BY name')
        return [row[0] for row in self.cursor.fetchall()]

    def add_relationship(self, parent_name, child_name):
        parent_id = self._get_member_id(parent_name)
        child_id = self._get_member_id(child_name)

        if parent_id is None or child_id is None:
            return False, "Cannot add relationship. One of the members does not exist."

        if parent_id == child_id:
            return False, "Cannot add relationship to self."

        if self._check_circular_relationship(child_id, parent_id):
            return False, "Cannot add relationship. It would create a circular relationship."

        try:
            self.cursor.execute('''
                INSERT INTO relationships (parent_id, child_id) VALUES (?, ?)
            ''', (parent_id, child_id))
            self.conn.commit()
            return True, f"Added relationship: {parent_name} -> {child_name}"
        except sqlite3.IntegrityError:
            return False, f"Relationship between '{parent_name}' and '{child_name}' already exists."

    def _check_circular_relationship(self, start_id, target_id):
        # Prevent circular relationships
        to_visit = [start_id]
        visited = set()
        while to_visit:
            current_id = to_visit.pop()
            if current_id == target_id:
                return True
            visited.add(current_id)
            self.cursor.execute('SELECT child_id FROM relationships WHERE parent_id = ?', (current_id,))
            children = [row[0] for row in self.cursor.fetchall()]
            to_visit.extend(child for child in children if child not in visited)
        return False

    def get_family_tree(self):
        # Build the family tree as a nested dictionary
        def build_tree(person_id):
            self.cursor.execute('''
                SELECT m.id, m.name FROM members m
                INNER JOIN relationships r ON m.id = r.child_id
                WHERE r.parent_id = ?
            ''', (person_id,))
            children = self.cursor.fetchall()
            return {name: build_tree(child_id) for child_id, name in children}

        # Find all root members (members without parents)
        self.cursor.execute('''
            SELECT m.id, m.name FROM members m
            WHERE m.id NOT IN (SELECT child_id FROM relationships)
        ''')
        roots = self.cursor.fetchall()
        family_tree = {}
        for root_id, root_name in roots:
            family_tree[root_name] = build_tree(root_id)
        return family_tree

    def visualize_tree(self):
        if not GRAPHVIZ_INSTALLED:
            messagebox.showerror("Graphviz Not Installed", "Graphviz library is not installed.")
            return

        dot = Digraph(comment='Family Tree')

        # Add nodes for each member with attributes
        self.cursor.execute('SELECT id, name, gender, birth_date FROM members')
        members = self.cursor.fetchall()
        for member_id, name, gender, birth_date in members:
            label = f"{name}"
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
        self.cursor.execute('SELECT parent_id, child_id FROM relationships')
        relationships = self.cursor.fetchall()
        for parent_id, child_id in relationships:
            dot.edge(str(parent_id), str(child_id))

        dot.render('family_tree.gv', view=True)

# Validation function for dates
def validate_date(date_text):
    if not date_text:
        return None
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_text):
        return date_text
    else:
        return None

# GUI Application Class
class FamilyTreeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Family Tree App")
        self.geometry("600x400")

        # Database connection
        self.conn = sqlite3.connect('family_tree.db')
        self.family_tree = FamilyTree(self.conn)

        # Create the GUI components
        self.create_widgets()

    def create_widgets(self):
        # Tabs
        self.tabControl = ttk.Notebook(self)
        self.tabControl.pack(expand=1, fill="both")

        # Tab for Members
        self.members_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.members_tab, text='Members')

        # Tab for Relationships
        self.relationships_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.relationships_tab, text='Relationships')

        # Tab for Family Tree
        self.tree_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tree_tab, text='Family Tree')

        # Members Tab Components
        self.create_members_tab()

        # Relationships Tab Components
        self.create_relationships_tab()

        # Family Tree Tab Components
        self.create_tree_tab()

        # Menu Bar
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Visualization Menu
        vis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualization", menu=vis_menu)
        vis_menu.add_command(label="Visualize Family Tree", command=self.family_tree.visualize_tree)

    def create_members_tab(self):
        # Labels and Entries for member details
        tk.Label(self.members_tab, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self.members_tab, text="Gender:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self.members_tab, text="Birth Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.name_entry = tk.Entry(self.members_tab)
        self.gender_entry = tk.Entry(self.members_tab)
        self.birth_date_entry = tk.Entry(self.members_tab)

        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.gender_entry.grid(row=1, column=1, padx=10, pady=10)
        self.birth_date_entry.grid(row=2, column=1, padx=10, pady=10)

        # Add Member Button
        add_member_btn = tk.Button(self.members_tab, text="Add Member", command=self.add_member)
        add_member_btn.grid(row=3, column=0, columnspan=2, pady=20)

    def create_relationships_tab(self):
        # Labels
        tk.Label(self.relationships_tab, text="Parent:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self.relationships_tab, text="Child:").grid(row=1, column=0, padx=10, pady=10, sticky="e")

        # Dropdowns for existing members
        self.parent_var = tk.StringVar()
        self.child_var = tk.StringVar()

        self.parent_menu = ttk.Combobox(self.relationships_tab, textvariable=self.parent_var)
        self.child_menu = ttk.Combobox(self.relationships_tab, textvariable=self.child_var)

        self.update_member_lists()

        self.parent_menu.grid(row=0, column=1, padx=10, pady=10)
        self.child_menu.grid(row=1, column=1, padx=10, pady=10)

        # Add Relationship Button
        add_rel_btn = tk.Button(self.relationships_tab, text="Add Relationship", command=self.add_relationship)
        add_rel_btn.grid(row=2, column=0, columnspan=2, pady=20)

    def create_tree_tab(self):
        # Tree Display
        self.tree_display = tk.Text(self.tree_tab, wrap='none')
        self.tree_display.pack(expand=1, fill='both')

        # Refresh Button
        refresh_btn = tk.Button(self.tree_tab, text="Refresh Tree", command=self.display_family_tree)
        refresh_btn.pack(pady=10)

        # Initially display the tree
        self.display_family_tree()

    def add_member(self):
        name = self.name_entry.get().strip()
        gender = self.gender_entry.get().strip()
        birth_date = self.birth_date_entry.get().strip()

        if not name:
            messagebox.showerror("Input Error", "Name cannot be empty.")
            return

        if birth_date and not validate_date(birth_date):
            messagebox.showerror("Input Error", "Birth date must be in YYYY-MM-DD format.")
            return

        success, message = self.family_tree.add_member(name, gender, birth_date)
        if success:
            messagebox.showinfo("Success", message)
            self.update_member_lists()
            # Clear inputs
            self.name_entry.delete(0, tk.END)
            self.gender_entry.delete(0, tk.END)
            self.birth_date_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)

    def update_member_lists(self):
        members = self.family_tree.get_members()
        self.parent_menu['values'] = members
        self.child_menu['values'] = members

    def add_relationship(self):
        parent_name = self.parent_var.get()
        child_name = self.child_var.get()

        if not parent_name or not child_name:
            messagebox.showerror("Input Error", "Parent and child must be selected.")
            return

        success, message = self.family_tree.add_relationship(parent_name, child_name)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def display_family_tree(self):
        family_tree = self.family_tree.get_family_tree()
        self.tree_display.delete('1.0', tk.END)
        self._display_tree_recursive(family_tree)

    def _display_tree_recursive(self, tree, level=0):
        for name, children in tree.items():
            self.tree_display.insert(tk.END, '    ' * level + f"- {name}\n")
            self._display_tree_recursive(children, level + 1)

    def on_closing(self):
        self.conn.close()
        self.destroy()

def main():
    app = FamilyTreeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
