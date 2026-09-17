import os
import re

# ================= 配置区 =================
IGNORE_DIRS = {
    '.git', '.idea', '.vscode', '__pycache__', 'node_modules',
    'venv', '.venv', 'env', 'dist', 'build', '.next', '.nuxt',
    'target', 'out', '.pytest_cache', '.mypy_cache', 'logs','docker'
}

SCRIPT_NAME = os.path.basename(__file__)
OUTPUT_FILE = 'PROJECT_FILES.md'

IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db'
}
# ==========================================

# 匹配形如: "├── foo.py    # 这是说明"  或  "└── foo.py  # 说明"
ANNOTATION_PATTERN = re.compile(r'^(?P<prefix>.*?)(?P<name>[\w\.\-]+)/?\s*#\s*(?P<note>.+?)\s*$')


def load_annotations_from_md(md_path):
    """
    从已有的 PROJECT_FILES.md 里解析出 {相对路径: 注解}
    用树形前缀 + 文件名拼接出相对路径
    """
    if not os.path.exists(md_path):
        return {}

    annotations = {}
    # 用一个栈维护当前目录路径
    stack = []

    with open(md_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            if not line.strip():
                continue
            # 只处理带树形连接符的行
            if '├── ' not in line and '└── ' not in line:
                continue

            # 通过 "│   " / "    " 数量推断层级
            # 找到连接符位置
            idx = line.find('├── ')
            if idx == -1:
                idx = line.find('└── ')
            prefix_part = line[:idx]
            content_part = line[idx + 4:]

            # 层级 = prefix 里 "│" 或 "    " 的组数
            level = prefix_part.count('│   ') + (len(prefix_part) - prefix_part.count('│   ') * 4) // 4

            # 拆出名字和注解
            name = content_part
            note = ''
            if '#' in content_part:
                name, note = content_part.split('#', 1)
                name = name.strip()
                note = note.strip()
            else:
                name = content_part.strip()

            is_dir = name.endswith('/')
            name_clean = name.rstrip('/')

            # 调整栈
            stack = stack[:level]
            if is_dir:
                stack.append(name_clean)
            else:
                rel_path = '/'.join(stack + [name_clean])
                if note:
                    annotations[rel_path] = note

    return annotations


def build_tree(root_dir='.'):
    """递归构建目录树结构，同时收集所有相对路径"""
    all_paths = []

    def _walk(path, rel):
        entries = []
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return entries

        dirs = [i for i in items if os.path.isdir(os.path.join(path, i)) and i not in IGNORE_DIRS]
        files = [i for i in items if os.path.isfile(os.path.join(path, i)) and i not in IGNORE_FILES]

        for d in dirs:
            child_rel = f'{rel}/{d}' if rel else d
            children = _walk(os.path.join(path, d), child_rel)
            entries.append({'name': d, 'type': 'dir', 'children': children, 'rel': child_rel})

        for f in files:
            file_rel = f'{rel}/{f}' if rel else f
            all_paths.append(file_rel)
            entries.append({'name': f, 'type': 'file', 'children': [], 'rel': file_rel})

        return entries

    tree = _walk(root_dir, '')
    return tree, all_paths


def render_tree(entries, annotations, prefix='', is_root=True, lines=None):
    """渲染树，文件后追加注解"""
    if lines is None:
        lines = []

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)

        if is_root:
            connector = '├── ' if not is_last else '└── '
            child_prefix = '│   ' if not is_last else '    '
        else:
            connector = prefix + ('├── ' if not is_last else '└── ')
            child_prefix = prefix + ('│   ' if not is_last else '    ')

        if entry['type'] == 'dir':
            lines.append(f'{connector}{entry["name"]}/')
            render_tree(entry['children'], annotations, child_prefix, is_root=False, lines=lines)
        else:
            note = annotations.get(entry['rel'], '')
            if note:
                lines.append(f'{connector}{entry["name"]}    # {note}')
            else:
                lines.append(f'{connector}{entry["name"]}')

    return lines


def main():
    # 1. 先读旧的 PROJECT_FILES.md，拿到注解
    annotations = load_annotations_from_md(OUTPUT_FILE)
    print(f'📥 从 {OUTPUT_FILE} 读回 {len(annotations)} 条注解')

    # 2. 重新扫描目录
    tree, all_paths = build_tree('.')

    # 3. 清理已不存在的文件的注解
    annotations = {k: v for k, v in annotations.items() if k in all_paths}

    # 4. 渲染
    lines = ['项目根目录/']
    render_tree(tree, annotations, is_root=True, lines=lines)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # 5. 提示哪些文件还没注解
    missing = [p for p in all_paths if p not in annotations]
    print(f'✅ 已生成：{OUTPUT_FILE}')
    if missing:
        print(f'⚠️  以下 {len(missing)} 个文件还没有注解，建议补上：')
        for p in missing:
            print(f'   - {p}')
    else:
        print('🎉 所有文件都已有注解')


if __name__ == '__main__':
    main()