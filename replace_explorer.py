import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

# Add import
import_line = "import OwnershipExplorer from './OwnershipExplorer';\n"
if "import OwnershipExplorer" not in content:
    content = content.replace("import { useState, useEffect } from 'react'", "import { useState, useEffect } from 'react'\n" + import_line)

# Find the activeTab block for Ownership Explorer
start_idx = content.find("{activeTab === 'Ownership Explorer' && (")
if start_idx != -1:
    end_idx = content.find(")}", start_idx) + 2
    new_ui = "{activeTab === 'Ownership Explorer' && <OwnershipExplorer />}"
    content = content[:start_idx] + new_ui + content[end_idx:]
    
with open('web/src/main.tsx', 'w') as f:
    f.write(content)
