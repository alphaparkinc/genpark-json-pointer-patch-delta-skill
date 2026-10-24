"""Example usage for GenPark JSON Pointer Patch Delta."""
from client import JSONPointerPatchDelta

def main():
    state_v1 = {"agent": {"status": "idle", "tasks": ["fetch_data"]}}
    state_v2 = {"agent": {"status": "running", "tasks": ["fetch_data", "parse_json"], "priority": 1}}

    print("Computing RFC 6902 Patch Delta between Agent States:")
    patch = JSONPointerPatchDelta.compute_patch(state_v1, state_v2)
    for op in patch:
        print(f" - {op['op']} at '{op['path']}': {op.get('value')}")

    print("
Applying Patch to state_v1:")
    reconstructed = JSONPointerPatchDelta.apply_patch(state_v1, patch)
    print("Reconstructed matches state_v2:", reconstructed == state_v2)

    val = JSONPointerPatchDelta.resolve_pointer(reconstructed, "/agent/status")
    print("Resolved /agent/status:", val)

if __name__ == "__main__":
    main()
