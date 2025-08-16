import os
import shutil
import javalang

OUTPUT_DIR = "CombinedAPI/src/main"

sources = {
    r"Latest\java\noppes\npcs\api": { # New API
        "description": "Latest version of CustomNpcs+ API",
        "priority": 2,
        "destination": r"java\noppes\npcs\api"
    },
    r"Latest\java\net\minecraft": { # New API
        "description": "Latest version of CustomNpcs+ API",
        "priority": 3,
        "destination": r"java\net\minecraft"
    },
    r"Extended Scripts Main\src\main\java\noppes\npcs\api": { # CustomNpcs+ older, commented API
        "description": "Older, but better commented version of CustomNpcs+ API",
        "priority": 1,
        "destination": r"java\noppes\npcs\api"
    },
    r"Extended Scripts Main\src\main\java\com\veil\extendedscripts\extendedapi": { # Base Extended API
        "description": "ExtendedScripts base API",
        "priority": 4,
        "destination": r"java\com\veil\extendedscripts\extendedapi"
    },
    r"Extended Scripts Main\src\main\java\noppes\npcs\extendedapi": { # Extended CustomNpcs+ API
        "description": "ExtendedScripts CustomNpcs+ Extensions",
        "priority": 5,
        "destination": r"java\noppes\npcs\api"
    }
}

def format_modifiers(mods):
    if not mods:
        return ""
    return " ".join(sorted(mods))

def format_type(t):
    if not t:
        return "void"
    try:
        # Handles simple types and generic names
        return t.name
    except AttributeError:
        return str(t)
    
def format_class(c):
    doc = format_doc(c)
    decl = f"{' '.join(c.modifiers)} class {c.name}"
    if c.extends:
        decl += f" extends {c.extends.name}"
    if c.implements:
        decl += " implements " + ", ".join([i.name for i in c.implements])
    return (doc + "\n" if doc else "") + decl + " {"

def format_method(m):
    doc = format_doc(m)
    params = []
    for p in m.parameters:
        dims = p.type.dimensions
        if isinstance(dims, list):
            dims = len(dims)
        elif dims is None:
            dims = 0
        param_type = p.type.name + "[]" * dims
        params.append(param_type + " " + p.name)

    throws = ""
    if m.throws:
        throws = " throws " + ", ".join(m.throws)

    header = f"    {' '.join(m.modifiers)}{" " if m.modifiers else ""}{m.return_type.name if m.return_type else 'void'} {m.name}({', '.join(params)}){throws};\n"
    return (doc + "\n" if doc else "") + header

def format_field(f):
    mods = format_modifiers(f.modifiers)
    ftype = format_type(f.type)
    decls = []
    for v in f.declarators:
        decl = v.name
        # FIX: Correctly handle initializers
        if v.initializer:
            if isinstance(v.initializer, javalang.tree.Literal):
                decl += f" = {v.initializer.value}"
            else:
                decl += " = /* complex initializer */"
        decls.append(decl)
    return f"    {mods} {ftype} {', '.join(decls)};"

def get_java_files(base_dir):
    """Recursively yield all .java files from base_dir."""
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".java"):
                yield os.path.join(root, f)

def format_doc(node):
    """Return the Javadoc comment for a node if it has one."""
    if hasattr(node, "documentation") and node.documentation:
        # Start with the opening of the Javadoc
        formatted_lines = ["    /**"]
        
        # Add each line of the original comment, prefixed with ' * '
        for line in node.documentation.strip().splitlines():
            # Strip any existing comment markers to avoid duplication
            clean_line = line.strip().lstrip('/*').rstrip('*/').strip()
            formatted_lines.append(f"     * {clean_line}")

        real_formatted_lines = []
        for line in formatted_lines:
            if line.strip() != "*" and line.strip() != "":
                real_formatted_lines.append(line)
            
        # Close the Javadoc
        real_formatted_lines.append("     */")
        return "\n".join(real_formatted_lines)
    return ""


def parse_java_file(filepath):
    """Return AST, raw code, and line-split version."""
    with open(filepath, encoding="utf-8") as f:
        code = f.read()
    tree = javalang.parse.parse(code)
    return tree, code, code.splitlines()


def extract_info(tree, filepath=None):
    """Extract imports, class/interface declaration, members."""
    imports = [imp.path for imp in tree.imports]

    class_decl = None
    for path, node in tree:
        if isinstance(node, (javalang.tree.ClassDeclaration, javalang.tree.InterfaceDeclaration)):
            class_decl = node
            break

    if class_decl is None and filepath:
        print(f"[WARN] No class/interface found in {filepath}")

    members = []
    if class_decl:
        for m in class_decl.body:
            if isinstance(m, (javalang.tree.MethodDeclaration, javalang.tree.FieldDeclaration)):
                members.append(m)

    return imports, class_decl, members


def copy_highest_priority(src, dest):
    """Copy entire directory as baseline."""
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def merge_sources(sources_sorted):
    """Main merging routine."""
    # Copy highest priority first
    highest_src, highest_meta = sources_sorted[0]
    dest_root = os.path.join(OUTPUT_DIR, highest_meta["destination"])
    print("Copying highest priority:", highest_meta["description"])
    copy_highest_priority(highest_src, dest_root)

    # Process subsequent ones
    for src, meta in sources_sorted[1:]:
        count = 0
        dest_root = os.path.join(OUTPUT_DIR, meta["destination"])

        for java_file in get_java_files(src):
            count += 1
            tree, code, lines = parse_java_file(java_file)
            imports, class_decl, members = extract_info(tree)
            if not class_decl:
                print(f"Skipping {java_file} - no class found")
                continue

            rel_path = os.path.relpath(java_file, src)
            out_file = os.path.join(dest_root, rel_path)

            if not os.path.exists(out_file):
                # If file doesn't exist yet, copy whole thing
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                shutil.copy(java_file, out_file)
                # print(f"Copying {java_file}")
                continue

            # Merge into existing file
            out_tree, out_code, out_lines = parse_java_file(out_file)
            out_imports, out_class, out_members = extract_info(out_tree)

            # Merge imports
            new_imports = [imp for imp in imports if imp not in out_imports]

            # Merge members
            out_signatures = {get_signature(m) for m in out_members}
            new_members = [m for m in members if get_signature(m) not in out_signatures]
            
            # Write merged version
            merged_code = rebuild_code(out_tree, out_code, new_imports, new_members)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(merged_code)

        if count == 0:
            print("No .java files found in", meta["description"])
        else:
            print("Merging:", meta["description"])


def get_signature(member):
    """Return a string signature for a method or field."""
    if isinstance(member, javalang.tree.MethodDeclaration):
        params = []
        for p in member.parameters:
            try:
                params.append(p.type.name if p.type else "unknown")
            except AttributeError:
                params.append("unknown")
        return f"method:{member.name}({','.join(params)})"
    elif isinstance(member, javalang.tree.FieldDeclaration):
        return "field:" + ",".join([v.name for v in member.declarators])
    return "unknown"


def rebuild_code(tree, original_code, new_imports, new_members):
    """
    Rebuild file:
    - Insert new imports after existing ones
    - Append new members at end of class body
    """
    lines = original_code.splitlines()

    # Insert imports
    if new_imports:
        last_import = 0
        for i, l in enumerate(lines):
            if l.strip().startswith("import "):
                last_import = i
        for imp in new_imports:
            lines.insert(last_import + 1, f"import {imp};")

    # Append new members before final }
    if new_members:
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "}":
                insert_idx = i
                break
        else:
            insert_idx = len(lines)

        lines.insert(insert_idx, "")
        insert_idx += 1

        for m in new_members:
            if isinstance(m, javalang.tree.MethodDeclaration):
                lines.insert(insert_idx, format_method(m))
            elif isinstance(m, javalang.tree.FieldDeclaration):
                lines.insert(insert_idx, format_field(m))

    return "\n".join(lines)


def main():
    # First delete existing combined API
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    # Sort sources by priority
    sorted_sources = sorted(sources.items(), key=lambda kv: kv[1]["priority"])
    merge_sources(sorted_sources)
    print(f"Combined API written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
