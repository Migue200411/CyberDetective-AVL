# avl_tree.py - Árbol AVL para organizar casos de ciberacoso

class CaseNode:
    """Nodo del árbol AVL que representa un caso de ciberacoso"""
    def __init__(self, case_id, case_type, evidence_list, law, penalty, description=""):
        self.case_id = case_id
        self.case_type = case_type
        self.evidence_list = evidence_list
        self.law = law
        self.penalty = penalty
        self.description = description
        self.left = None
        self.right = None
        self.height = 1
        # Posición para visualización
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f"CaseNode(id={self.case_id}, tipo={self.case_type})"


class AVLTree:
    """Árbol AVL auto-balanceado para gestión eficiente de casos"""

    def __init__(self):
        self.root = None
        self.rotation_log = []  # registro de rotaciones para mostrar al jugador

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node):
        if node:
            node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, z):
        """Rotación a la derecha (caso LL)"""
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        self._update_height(z)
        self._update_height(y)
        self.rotation_log.append(f"Rotación Derecha en nodo {z.case_id} → árbol re-balanceado")
        return y

    def _rotate_left(self, z):
        """Rotación a la izquierda (caso RR)"""
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        self._update_height(z)
        self._update_height(y)
        self.rotation_log.append(f"Rotación Izquierda en nodo {z.case_id} → árbol re-balanceado")
        return y

    def _insert_recursive(self, root, node):
        """Inserción recursiva con re-balanceo automático"""
        if not root:
            return node
        if node.case_id < root.case_id:
            root.left = self._insert_recursive(root.left, node)
        elif node.case_id > root.case_id:
            root.right = self._insert_recursive(root.right, node)
        else:
            return root  # ID duplicado, no insertar

        self._update_height(root)
        bf = self._balance_factor(root)

        # Caso LL - desbalance izquierda-izquierda
        if bf > 1 and node.case_id < root.left.case_id:
            return self._rotate_right(root)
        # Caso RR - desbalance derecha-derecha
        if bf < -1 and node.case_id > root.right.case_id:
            return self._rotate_left(root)
        # Caso LR - desbalance izquierda-derecha
        if bf > 1 and node.case_id > root.left.case_id:
            root.left = self._rotate_left(root.left)
            return self._rotate_right(root)
        # Caso RL - desbalance derecha-izquierda
        if bf < -1 and node.case_id < root.right.case_id:
            root.right = self._rotate_right(root.right)
            return self._rotate_left(root)

        return root

    def insert(self, case_id, case_type, evidence_list, law, penalty, description=""):
        """Inserta un nuevo caso en el árbol AVL"""
        new_node = CaseNode(case_id, case_type, evidence_list, law, penalty, description)
        self.root = self._insert_recursive(self.root, new_node)
        return new_node

    def inorder(self):
        """Recorrido inorden del árbol"""
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node)
            self._inorder_recursive(node.right, result)

    def calculate_positions(self, node, x, y, x_offset):
        """Calcula las posiciones (x, y) de cada nodo para renderizar el árbol"""
        if not node:
            return
        node.x = x
        node.y = y
        half = max(x_offset // 2, 30)
        self.calculate_positions(node.left, x - x_offset, y + 90, half)
        self.calculate_positions(node.right, x + x_offset, y + 90, half)

    def get_all_nodes(self):
        """Retorna todos los nodos en lista"""
        nodes = []
        self._collect_nodes(self.root, nodes)
        return nodes

    def _collect_nodes(self, node, result):
        if node:
            result.append(node)
            self._collect_nodes(node.left, result)
            self._collect_nodes(node.right, result)

    def get_depth(self):
        """Retorna la profundidad total del árbol"""
        return self._height(self.root)
