# FamilyTree
A console-based application for creating and managing a family tree using Python and SQLite. This app allows users to add family members, define parent-child relationships, and display the family tree hierarchy with data persistence through an SQLite database.


Thought for a few seconds

Family Tree App in Python with SQLite
A console-based application for creating and managing a family tree using Python and SQLite. This app allows users to add family members, define parent-child relationships, and display the family tree hierarchy with data persistence through an SQLite database.

Features
Add Family Members: Input names to add new members to the family tree.
Define Relationships: Establish parent-child relationships between members.
Display Family Tree: View the family tree hierarchy in the console.
Data Persistence: All data is stored in an SQLite database for persistent storage.
Visualize Family Tree (Optional): Generate a graphical representation of the family tree using Graphviz.
Requirements
Python 3.x
SQLite3 (included with Python)
Graphviz (optional, for visualization)
Install the Python package: pip install graphviz
Install Graphviz system package from Graphviz Download
How to Use
Clone the Repository:

bash
Copy code
git clone https://github.com/yourusername/family-tree-app.git
cd family-tree-app
Install Dependencies (if using visualization):

bash
Copy code
pip install graphviz
Run the Application:

bash
Copy code
python family_tree_app.py
Follow the On-Screen Menu:

Add Member: Enter the name of the new family member.
Add Relationship: Specify the parent and child to define a relationship.
Display Family Tree: View the family tree in the console.
Visualize Family Tree: Generate and view a graphical representation (requires Graphviz).
Exit: Close the application.
Project Structure
family_tree_app.py: Main application script containing the classes and program loop.
family_tree.db: SQLite database file generated upon running the app.
README.md: Project description and usage instruction
