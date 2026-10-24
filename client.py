"""JSON Pointer Patch Delta.
100% Python Standard Library.
"""
from typing import Dict, Any, List

class JSONPointerPatchDelta:
    """RFC 6901 / RFC 6902 compliant JSON Pointer and JSON Patch delta computation engine."""

    @staticmethod
    def resolve_pointer(document: Any, pointer: str) -> Any:
        if pointer == "" or pointer == "/":
            return document
        if not pointer.startswith("/"):
            raise ValueError(f"Invalid JSON Pointer: '{pointer}', must start with '/'")

        tokens = [t.replace("~1", "/").replace("~0", "~") for t in pointer[1:].split("/")]
        curr = document
        for t in tokens:
            if isinstance(curr, dict):
                if t not in curr:
                    raise KeyError(f"Property '{t}' not found in dict")
                curr = curr[t]
            elif isinstance(curr, list):
                if not t.isdigit():
                    raise IndexError(f"Array index must be integer, got '{t}'")
                idx = int(t)
                if idx < 0 or idx >= len(curr):
                    raise IndexError(f"Array index {idx} out of range (length {len(curr)})")
                curr = curr[idx]
            else:
                raise TypeError(f"Cannot traverse into primitive {type(curr).__name__}")
        return curr

    @classmethod
    def compute_patch(cls, original: Any, modified: Any, path_prefix: str = "") -> List[Dict[str, Any]]:
        patch = []
        if type(original) != type(modified):
            return [{"op": "replace", "path": path_prefix or "/", "value": modified}]

        if isinstance(original, dict):
            for k in original:
                if k not in modified:
                    p = f"{path_prefix}/{k.replace('~', '~0').replace('/', '~1')}"
                    patch.append({"op": "remove", "path": p})

            for k in modified:
                p = f"{path_prefix}/{k.replace('~', '~0').replace('/', '~1')}"
                if k not in original:
                    patch.append({"op": "add", "path": p, "value": modified[k]})
                elif original[k] != modified[k]:
                    patch.extend(cls.compute_patch(original[k], modified[k], p))

        elif isinstance(original, list):
            if original != modified:
                patch.append({"op": "replace", "path": path_prefix or "/", "value": modified})
        else:
            if original != modified:
                patch.append({"op": "replace", "path": path_prefix or "/", "value": modified})

        return patch

    @classmethod
    def apply_patch(cls, document: Any, patch: List[Dict[str, Any]]) -> Any:
        import copy
        doc = copy.deepcopy(document)

        for operation in patch:
            op = operation.get("op")
            path = operation.get("path", "")
            val = operation.get("value")

            if path == "" or path == "/":
                if op in ("add", "replace"):
                    doc = val
                continue

            tokens = [t.replace("~1", "/").replace("~0", "~") for t in path[1:].split("/")]
            parent = doc
            for t in tokens[:-1]:
                if isinstance(parent, dict):
                    parent = parent[t]
                elif isinstance(parent, list):
                    parent = parent[int(t)]

            last_token = tokens[-1]
            if isinstance(parent, dict):
                if op in ("add", "replace"):
                    parent[last_token] = val
                elif op == "remove":
                    parent.pop(last_token, None)
            elif isinstance(parent, list):
                idx = int(last_token)
                if op == "add":
                    parent.insert(idx, val)
                elif op == "replace":
                    parent[idx] = val
                elif op == "remove":
                    parent.pop(idx)

        return doc
