
import ast
from dataclasses import dataclass, asdict


@dataclass
class ClassInfo:
    name: str
    bases: list[str]
    methods: list[str]
    attributes: list[str]


@dataclass
class Relationship:
    source: str
    target: str
    kind: str
    evidence: str


def get_name(node):
    """Convert a Python AST expression into a readable name."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return get_name(node.value) + "." + node.attr
    if isinstance(node, ast.Subscript):
        return get_name(node.value)
    if isinstance(node, ast.Call):
        return get_name(node.func)
    return ""


def analyze_code(source):
    tree = ast.parse(source)
    class_nodes = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]

    known = {node.name for node in class_nodes}
    classes = []
    relationships = []

    for node in class_nodes:
        bases = [
            get_name(base).split(".")[-1]
            for base in node.bases
            if get_name(base)
        ]

        methods = sorted({
            item.name
            for item in node.body
            if isinstance(
                item,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            )
        })

        attributes = set()

        for child in ast.walk(node):
            if isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name):
                    attributes.add(child.target.id)

            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        attributes.add(target.id)

                    elif (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                    ):
                        attributes.add(target.attr)

        classes.append(ClassInfo(
            name=node.name,
            bases=bases,
            methods=methods,
            attributes=sorted(attributes)
        ))

        # Detect inheritance relationships.
        for base in bases:
            if base in known and base != node.name:
                relationships.append(Relationship(
                    source=node.name,
                    target=base,
                    kind="inheritance",
                    evidence=f"{node.name} extends {base}"
                ))

        # Detect references to other known classes.
        references = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if child.id in known and child.id != node.name:
                    references.add(child.id)

            elif isinstance(child, ast.Attribute):
                if child.attr in known and child.attr != node.name:
                    references.add(child.attr)

        for target in references - set(bases):
            relationships.append(Relationship(
                source=node.name,
                target=target,
                kind="association",
                evidence=f"{node.name} references {target}"
            ))

    # Remove duplicate relationships.
    unique = {}
    for rel in relationships:
        key = (rel.source, rel.target, rel.kind)
        unique[key] = rel

    return classes, list(unique.values())


def generate_mermaid(classes, relationships):
    lines = ["classDiagram"]

    for cls in classes:
        lines.append(f"    class {cls.name} {{")

        for attr in cls.attributes:
            lines.append(f"        +{attr}")

        for method in cls.methods:
            lines.append(f"        +{method}()")

        lines.append("    }")

    for rel in relationships:
        if rel.kind == "inheritance":
            lines.append(
                f"    {rel.target} <|-- {rel.source}"
            )
        else:
            lines.append(
                f"    {rel.source} --> {rel.target} : uses"
            )

    return "\n".join(lines)


def export_data(classes, relationships):
    return {
        "classes": [asdict(c) for c in classes],
        "relationships": [asdict(r) for r in relationships]
    }
