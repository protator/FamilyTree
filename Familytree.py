import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

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
                birth_year INTEGER,
                birth_month INTEGER,
                birth_day INTEGER,
                mother_id INTEGER,
                father_id INTEGER,
                FOREIGN KEY(mother_id) REFERENCES members(id),
                FOREIGN KEY(father_id) REFERENCES members(id)
            )
        ''')

        # Create table for relationships
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member1_id INTEGER,
                member2_id INTEGER,
                relationship_type TEXT,
                FOREIGN KEY(member1_id) REFERENCES members(id),
                FOREIGN KEY(member2_id) REFERENCES members(id)
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

        # Tab4: Define Relationships
        self.tab4 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab4, text='Define Relationships')
        self.create_relationship_tab()

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
        self.gender_combo = ttk.Combobox(self.tab1, textvariable=self.gender_var, values=["Male", "Female", "Other"], state="readonly")
        self.gender_combo.grid(column=1, row=2, padx=10, pady=5)
        self.gender_combo.set('')  # Default to empty

        # Birth Year
        ttk.Label(self.tab1, text="Birth Year:").grid(column=0, row=3, padx=10, pady=5, sticky='W')
        self.birth_year_spin = ttk.Spinbox(self.tab1, from_=1900, to=2100, width=28)
        self.birth_year_spin.grid(column=1, row=3, padx=10, pady=5)

        # Birth Month
        ttk.Label(self.tab1, text="Birth Month:").grid(column=0, row=4, padx=10, pady=5, sticky='W')
        self.birth_month_spin = ttk.Spinbox(self.tab1, from_=1, to=12, width=28)
        self.birth_month_spin.grid(column=1, row=4, padx=10, pady=5)

        # Birth Day
        ttk.Label(self.tab1, text="Birth Day:").grid(column=0, row=5, padx=10, pady=5, sticky='W')
        self.birth_day_spin = ttk.Spinbox(self.tab1, from_=1, to=31, width=28)
        self.birth_day_spin.grid(column=1, row=5, padx=10, pady=5)

        # Mother's Full Name
        ttk.Label(self.tab1, text="Mother's Full Name:").grid(column=0, row=6, padx=10, pady=5, sticky='W')
        self.mother_name_entry = ttk.Entry(self.tab1, width=30)
        self.mother_name_entry.grid(column=1, row=6, padx=10, pady=5)

        # Father's Full Name
        ttk.Label(self.tab1, text="Father's Full Name:").grid(column=0, row=7, padx=10, pady=5, sticky='W')
        self.father_name_entry = ttk.Entry(self.tab1, width=30)
        self.father_name_entry.grid(column=1, row=7, padx=10, pady=5)

        # Add Member Button
        self.add_member_button = ttk.Button(self.tab1, text="Add Member", command=self.add_member)
        self.add_member_button.grid(column=1, row=8, padx=10, pady=10, sticky='E')

    def create_view_tree_tab(self):
        self.tree_text = tk.Text(self.tab2, wrap='none')
        self.tree_text.pack(expand=1, fill='both')

        # Refresh Button
        self.refresh_button = ttk.Button(self.tab2, text="Refresh Tree", command=self.display_tree)
        self.refresh_button.pack(pady=10)

    # The missing display_tree method
    def display_tree(self):
        self.tree_text.delete(1.0, tk.END)  # Clear previous content

        roots = self.get_roots()
        visited = set()

        # Recursively display the family tree
        for root_id, first_name, last_name in roots:
            full_name = f"{first_name} {last_name}"
            self.display_tree_recursive(root_id, full_name, 0, visited)

    def get_roots(self):
        """ Get members with no parents (root members) """
        self.cursor.execute('''
            SELECT id, first_name, last_name FROM members
            WHERE mother_id IS NULL AND father_id IS NULL
        ''')
        return self.cursor.fetchall()

    def display_tree_recursive(self, person_id, full_name, level, visited):
        """ Display tree recursively """
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

    def create_visualize_tab(self):
        # Create Canvas for visualization
        self.canvas = tk.Canvas(self.tab3, bg="white")
        self.canvas.pack(expand=True, fill='both')

        # Visualize Button
        self.visualize_button = ttk.Button(self.tab3, text="Visualize Family Tree", command=self.visualize_tree_canvas)
        self.visualize_button.pack(pady=20)

    # Adding the missing visualize_tree_canvas method
    def visualize_tree_canvas(self):
        self.canvas.delete("all")  # Clear canvas for fresh drawing
        roots = self.get_roots()
        visited = set()

        # Starting position for the root member
        for root_id, first_name, last_name in roots:
            self.visualize_tree_recursive(root_id, f"{first_name} {last_name}", 400, 50, visited)

    def visualize_tree_recursive(self, person_id, full_name, x, y, visited):
        if person_id in visited:
            return
        visited.add(person_id)

        node_width = 100
        self.canvas.create_text(x, y, text=full_name, tags="node")
        self.canvas.create_rectangle(x - node_width // 2, y - 15, x + node_width // 2, y + 15, outline="black", tags="node")

        # Get children of the current person
        self.cursor.execute('''
            SELECT id, first_name, last_name FROM members
            WHERE mother_id = ? OR father_id = ?
        ''', (person_id, person_id))
        children = self.cursor.fetchall()

        child_x_offset = 150
        child_y_offset = 100

        for i, (child_id, first_name, last_name) in enumerate(children):
            child_x = x + (i - len(children) // 2) * child_x_offset
            child_y = y + child_y_offset
            self.canvas.create_line(x, y + 15, child_x, child_y - 15)
            self.visualize_tree_recursive(child_id, f"{first_name} {last_name}", child_x, child_y, visited)

    def create_relationship_tab(self):
        # Member 1 Dropdown
        ttk.Label(self.tab4, text="Member 1:").grid(column=0, row=0, padx=10, pady=5, sticky='W')
        self.member1_combo = ttk.Combobox(self.tab4, width=30, state="readonly")
        self.member1_combo.grid(column=1, row=0, padx=10, pady=5)

        # Member 2 Dropdown
        ttk.Label(self.tab4, text="Member 2:").grid(column=0, row=1, padx=10, pady=5, sticky='W')
        self.member2_combo = ttk.Combobox(self.tab4, width=30, state="readonly")
        self.member2_combo.grid(column=1, row=1, padx=10, pady=5)

        # Relationship Type Entry
        ttk.Label(self.tab4, text="Relationship Type:").grid(column=0, row=2, padx=10, pady=5, sticky='W')
        self.relationship_type_entry = ttk.Entry(self.tab4, width=30)
        self.relationship_type_entry.grid(column=1, row=2, padx=10, pady=5)

        # Add Relationship Button
        self.add_relationship_button = ttk.Button(self.tab4, text="Add Relationship", command=self.add_relationship)
        self.add_relationship_button.grid(column=1, row=3, padx=10, pady=10, sticky='E')

        # Populate member combo boxes when switching to the relationship tab
        self.tab_control.bind("<<NotebookTabChanged>>", self.populate_member_combos)

    def populate_member_combos(self, event=None):
        if self.tab_control.index("current") == 3:  # Only populate if we're on the "Define Relationships" tab
            self.cursor.execute('SELECT id, first_name, last_name FROM members')
            members = self.cursor.fetchall()

            # Clear previous values
            member_names = [f"{first_name} {last_name}" for _, first_name, last_name in members]
            self.member1_combo['values'] = member_names
            self.member2_combo['values'] = member_names

    # Adding the missing add_relationship method
    def add_relationship(self):
        member1_full_name = self.member1_combo.get().strip()
        member2_full_name = self.member2_combo.get().strip()
        relationship_type = self.relationship_type_entry.get().strip()

        if not member1_full_name or not member2_full_name or not relationship_type:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        member1_id = self._get_member_id_by_full_name(member1_full_name)
        member2_id = self._get_member_id_by_full_name(member2_full_name)

        if member1_id and member2_id:
            self.cursor.execute('''
                INSERT INTO relationships (member1_id, member2_id, relationship_type)
                VALUES (?, ?, ?)
            ''', (member1_id, member2_id, relationship_type))
            self.conn.commit()
            messagebox.showinfo("Success", f"Added relationship: {relationship_type} between {member1_full_name} and {member2_full_name}")
        else:
            messagebox.showerror("Error", "One or both members not found.")

    def add_member(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        if not first_name or not last_name:
            messagebox.showerror("Error", "First name and last name cannot be empty.")
            return

        gender = self.gender_var.get().strip() or None

        # Get and validate birth date components
        birth_year = self.birth_year_spin.get().strip()
        birth_month = self.birth_month_spin.get().strip()
        birth_day = self.birth_day_spin.get().strip()

        birth_year_int, birth_month_int, birth_day_int = self.validate_birth_date(birth_year, birth_month, birth_day)
        if birth_year_int is None:
            return  # Error message already shown in validate_birth_date

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
                INSERT INTO members (first_name, last_name, gender, birth_year, birth_month, birth_day, mother_id, father_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, gender, birth_year_int, birth_month_int, birth_day_int, mother_id, father_id))
            self.conn.commit()  # Ensure changes are saved to the database
            messagebox.showinfo("Success", f"Added member: {first_name} {last_name}")
            self.clear_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Member '{first_name} {last_name}' already exists.")

    def clear_entries(self):
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.gender_var.set('')
        self.birth_year_spin.delete(0, tk.END)
        self.birth_month_spin.delete(0, tk.END)
        self.birth_day_spin.delete(0, tk.END)
        self.mother_name_entry.delete(0, tk.END)
        self.father_name_entry.delete(0, tk.END)

    def validate_birth_date(self, year, month, day):
        # Ensure all fields are provided
        if not year or not month or not day:
            messagebox.showerror("Error", "Birth year, month, and day are required.")
            return None, None, None

        # Validate year
        try:
            birth_year_int = int(year)
            if not (1900 <= birth_year_int <= 2100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Birth year must be a number between 1900 and 2100.")
            return None, None, None

        # Validate month
        try:
            birth_month_int = int(month)
            if not (1 <= birth_month_int <= 12):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Birth month must be a number between 1 and 12.")
            return None, None, None

        # Validate day
        try:
            birth_day_int = int(day)
            if not (1 <= birth_day_int <= 31):
                raise ValueError
            # Optional: More precise day validation based on month and leap years
        except ValueError:
            messagebox.showerror("Error", "Birth day must be a number between 1 and 31.")
            return None, None, None

        return birth_year_int, birth_month_int, birth_day_int

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

    def on_closing(self):
        self.conn.commit()  # Ensure any pending transactions are committed
        self.conn.close()  # Close the database connection properly to save data
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FamilyTreeApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
