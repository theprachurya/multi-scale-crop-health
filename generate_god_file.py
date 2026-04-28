import os
import glob

exclude_dirs = {'venv_cuda', '.git', '__pycache__', 'outputs', 'data', 'Supporting Documents', 'notebooks'}
exclude_files = {'generate_arch.py', 'find_zips.py', 'architecture_diagram.png', 'test.jpg', 'read_sprint.py', 'update_docs.py', 'god_file.md', 'z.json', 'z.txt', 'crash.log', 'log.txt', 'PROJECT_RECREATION_GUIDE.md', 'generate_god_file.py', 'test_god_file.py'}
allowed_exts = {'.py', '.txt', '.yaml', '.md', '.json', '.html', '.css', '.js', '.ps1', '.sh', '.tex', ''}

project_dir = r'c:\Users\zen\Desktop\zapder\minor project\multi-scale-crop-health'

def get_tree(dir_path, prefix=''):
    tree_str = ''
    try:
        items = os.listdir(dir_path)
    except Exception:
        return ''
    items = sorted([item for item in items if item not in exclude_dirs and item not in exclude_files])
    
    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = (i == len(items) - 1)
        tree_str += prefix + ('└── ' if is_last else '├── ') + item + '\n'
        if os.path.isdir(path):
            tree_str += get_tree(path, prefix + ('    ' if is_last else '│   '))
    return tree_str

god_file = os.path.join(project_dir, 'PROJECT_RECREATION_GUIDE.md')
with open(god_file, 'w', encoding='utf-8') as gf:
    gf.write('# 🌾 Multi-Scale Crop Health Classification — Project Recreation Guide\n\n')
    
    # Write the Knowledge Base for project information
    kb_path = os.path.join(project_dir, 'KNOWLEDGE_BASE.md')
    if os.path.exists(kb_path):
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                gf.write(f.read())
                gf.write('\n\n---\n\n')
        except Exception as e:
            gf.write(f'Error reading KB: {e}\n\n')
            
    gf.write('## 19. Complete File Tree\n\n')
    gf.write('```\n')
    gf.write(get_tree(project_dir))
    gf.write('```\n\n---\n\n')
    
    gf.write('## 20. Codebase / File Contents\n\n')
    gf.write('The following section contains the full code logic and contents for every file in the project. These files allow for a perfect recreation of the project logic, architecture, and configuration.\n\n')
    
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            ext = os.path.splitext(file)[1]
            if ext not in allowed_exts:
                if file != '.gitignore':
                    continue
            
            filepath = os.path.join(root, file)
            # if it's the knowledge base or current file, we can skip printing its code since KB is above
            if file == 'KNOWLEDGE_BASE.md':
                continue
            if file == 'PROJECT_RECREATION_GUIDE.md':
                continue
            
            rel_path = os.path.relpath(filepath, project_dir)
            gf.write(f'### File: `{rel_path}`\n\n')
            
            lang = 'python' if ext == '.py' else 'yaml' if ext == '.yaml' else 'json' if ext == '.json' else 'html' if ext == '.html' else 'css' if ext == '.css' else 'javascript' if ext == '.js' else 'bash' if ext == '.sh' else 'powershell' if ext == '.ps1' else 'tex' if ext == '.tex' else ''
            lang = 'text' if not lang else lang
            if file == '.gitignore':
                lang = 'text'
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                gf.write(f'```{lang}\n')
                gf.write(content)
                gf.write('\n```\n\n')
            except Exception as e:
                gf.write(f'> Error reading file: {e}\n\n')
                
print('Generated God File: PROJECT_RECREATION_GUIDE.md')
