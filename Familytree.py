import sqlite3

class Person:
    def __init__(self, name, person_id):
        self.id = person_id
        self.name = name

class FamilyTree:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = self.conn.cursor()

    def add_member(self, name):
        try:
            self.cursor.execute('INSERT INTO members (name) VALUES (?)', (name,))
            self.conn.commit()
            print(f"Added member: {name}")
        except sqlite3.IntegrityError:
            print(f"Member {name} already exists.")

    def _get_member_id(self, name):
        self.cursor.execute('SELECT id FROM members WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"Member {name} not found.")
            return None

    def add_relationship(self, parent_name, child_name):
        parent_id = self._get_member_id(parent_name)
        child_id = self._get_member_id(child_name)

        if parent_id and child_id:
            try:
                self.cursor.execute('INSERT INTO relationships (parent_id, child_id) VALUES (?, ?)',
                                    (parent_id, child_id))
                self.conn.commit()
                print(f"Added relationship: {parent_name} -> {child_name}")
            except sqlite3.IntegrityError:
                print(f"Relationship between {parent_name} and {child_name} already exists.")
        else:
            print("Cannot add relationship. One of the members does not exist.")

    def display_tree(self):
        self.cursor.execute('''
            SELECT m.id, m.name FROM members m
            WHERE m.id NOT IN (SELECT child_id FROM relationships)
        ''')
        roots = self.cursor.fetchall()
        visited = set()
        for root_id, root_name in roots:
            self._display_tree_recursive(root_id, root_name, 0, visited)

    def _display_tree_recursive(self, person_id, person_name, level, visited):
        if person_id in visited:
            return
        visited.add(person_id)
        print('    ' * level + f"- {person_name}")
        self.cursor.execute('''
            SELECT m.id, m.name FROM members m
            INNER JOIN relationships r ON m.id = r.child_id
            WHERE r.parent_id = ?
        ''', (person_id,))
        children = self.cursor.fetchall()
        for child_id, child_name in children:
            self._display_tree_recursive(child_id, child_name, level + 1, visited)

def setup_database():
    conn = sqlite3.connect('family_tree.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            parent_id INTEGER NOT NULL,
            child_id INTEGER NOT NULL,
            FOREIGN KEY(parent_id) REFERENCES members(id),
            FOREIGN KEY(child_id) REFERENCES members(id),
            PRIMARY KEY (parent_id, child_id)
        )
    ''')

    conn.commit()
    return conn

def main():
    conn = setup_database()
    family_tree = FamilyTree(conn)

    while True:
        print("\nFamily Tree App")
        print("1. Add Member")
        print("2. Add Relationship")
        print("3. Display Family Tree")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter the member's name: ").strip()
            if name:
                family_tree.add_member(name)
            else:
                print("Name cannot be empty.")
        elif choice == '2':
            parent_name = input("Enter the parent's name: ").strip()
            child_name = input("Enter the child's name: ").strip()
            if parent_name and child_name:
                family_tree.add_relationship(parent_name, child_name)
            else:
                print("Parent and child names cannot be empty.")
        elif choice == '3':
            print("\nFamily Tree:")
            family_tree.display_tree()
        elif choice == '4':
            print("Exiting the app.")
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == "__main__":
    main()
