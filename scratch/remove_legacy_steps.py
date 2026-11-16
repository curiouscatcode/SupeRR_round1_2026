import os
import shutil
import re

def cleanup_legacy_steps():
    print("=" * 80)
    print("CLEANUP: REMOVING LEGACY STEPS 11 THROUGH 16")
    print("=" * 80)

    target_dirs = []
    pattern = re.compile(r'^step_(\d+)')

    for base in ['src', 'outputs']:
        if not os.path.exists(base):
            continue
        for d in os.listdir(base):
            m = pattern.match(d)
            if m:
                step_val = int(m.group(1))
                if 11 <= step_val <= 16:
                    full = os.path.join(base, d)
                    if os.path.isdir(full):
                        target_dirs.append((full, step_val))

    print(f"Identified {len(target_dirs)} legacy directories for removal.")
    
    # Safety assertion: Ensure NO step_10 or lower directories are accidentally targeted
    for td, s_val in target_dirs:
        assert 11 <= s_val <= 16, f"FATAL: Protected directory targeted: {td} with step {s_val}"
        base_name = os.path.basename(td)
        assert 'step_10' not in base_name, f"FATAL: Protected directory targeted: {td}"
        assert not any(base_name.startswith(f'step_{i}_') for i in range(0, 11)), f"FATAL: Protected directory: {td}"

    removed_count = 0
    total_bytes_freed = 0

    for td, s_val in sorted(target_dirs, key=lambda x: x[0]):
        bytes_in_dir = sum(os.path.getsize(os.path.join(r, f)) for r, _, files in os.walk(td) for f in files)
        shutil.rmtree(td)
        removed_count += 1
        total_bytes_freed += bytes_in_dir
        print(f"[REMOVED] {td} ({bytes_in_dir / (1024*1024):.2f} MB)")

    print("-" * 80)
    print(f"CLEANUP COMPLETE: Removed {removed_count} directories. Freed {total_bytes_freed / (1024*1024):.2f} MB.")
    print("=" * 80)

if __name__ == '__main__':
    cleanup_legacy_steps()
