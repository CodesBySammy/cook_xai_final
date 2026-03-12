import ast

class RAGEngine:
    def extract_dependencies(self, raw_code: str) -> list:
        """Parses Python code to find integrated modules."""
        dependencies = []
        try:
            tree = ast.parse(raw_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    dependencies.append(node.module)
        except SyntaxError:
            pass
        return dependencies

rag_engine = RAGEngine()