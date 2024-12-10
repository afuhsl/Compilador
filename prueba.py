from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem

app = QApplication([])

tree = QTreeWidget()
tree.setHeaderLabel("Tree Example")

root = QTreeWidgetItem(tree, ["Root Node"])
child1 = QTreeWidgetItem(root, ["Child 1"])
QTreeWidgetItem(child1, ["Child 1.1"])
QTreeWidgetItem(child1, ["Child 1.2"])
child2 = QTreeWidgetItem(root, ["Child 2"])
QTreeWidgetItem(child2, ["Child 2.1"])

tree.show()
app.exec_()
