# **AGENT_USAGE.md — IntelliHub MCP Tool Usage Guide**  
_Standardized expectations and best practices for all AI agents interacting with the MonTamerGens IntelliHub._

---

## 🧭 **Purpose of This Guide**

This document defines **how agents should interact with the IntelliHub MCP Tool** to ensure:

- consistent behavior across agents  
- alignment with canonical project knowledge  
- safe and predictable tool usage  
- avoidance of hallucinated or inferred context  
- stable integration with the MonTamerGens architecture  

All agents must follow these guidelines when retrieving or reasoning over project documentation.

---

# 🧩 **1. Core Principles**

### **1.1 The IntelliHub is the single source of truth**  
Agents must treat all files within `/ai_context/` as canonical.  
If information is not present in the IntelliHub, agents must not assume or invent details.

### **1.2 The tool is read‑only**  
Agents must not attempt to modify, overwrite, or generate files through this tool.

### **1.3 Use explicit retrieval, not inference**  
Agents must call the appropriate function rather than relying on memory or assumptions.

### **1.4 Prefer direct file access over search when possible**  
If the agent knows the file name, it should call `read_file()` instead of `search()`.

---

# 🛠️ **2. Function Usage Guidelines**

## **2.1 `list_files()`**
Use this to:

- discover available documentation  
- verify file paths before calling `read_file()`  
- enumerate schemas or module purpose files  

Agents should not assume directory contents — always check.

---

## **2.2 `read_file(path)`**
Use this when:

- the agent knows the exact file needed  
- referencing architecture, lore, naming rules, or appendices  
- retrieving module documentation or schemas directly  

Agents must use **relative paths** exactly as returned by `list_files()`.

---

## **2.3 `search(query)`**
Use this when:

- the agent needs to locate where a concept is defined  
- the agent is unsure which file contains the information  
- cross‑referencing terminology or lore  

Agents must not rely solely on search results for authoritative definitions — after locating the file, call `read_file()` for full context.

---

## **2.4 `get_schema(name)`**
Use this when:

- validating YAML or Python data structures  
- generating new data that must conform to canonical schemas  
- checking field names, types, or constraints  

Agents must not invent schema fields or modify schema definitions.

---

## **2.5 `get_module_purpose(name)`**
Use this when:

- generating new modules  
- refactoring existing modules  
- understanding integration points  
- maintaining architectural consistency  

Agents must treat module purpose files as authoritative descriptions of module responsibilities.

---

## **2.6 `diagnose()`**
Use this when:

- verifying the integrity of the knowledge base  
- troubleshooting missing files or schemas  
- checking if the `ai_context` path is correctly configured  

Agents should call this if other tools return unexpected errors indicating missing files.

---

# 🧠 **3. Canonical Alignment Rules**

### **3.1 Never hallucinate missing architecture**
If the IntelliHub does not define a system, mechanic, or rule, agents must:

- state that the information is not present  
- request clarification or expansion from the user  
- avoid fabricating details  

---

### **3.2 Always cross‑reference related documents**
For example:

- architecture decisions → `architecture_overview.md`  
- lore concepts → `lore_core.md` + `appendices/A_appendix.md`  
- naming rules → `naming_conventions.md`  
- module behavior → `module_purposes/*.md`  
- data shapes → `schemas/*.md`  

Agents should combine these sources when reasoning.

---

### **3.3 Maintain consistency with naming conventions**
When generating:

- modules  
- functions  
- YAML keys  
- monster names  
- file names  

Agents must reference `naming_conventions.md` and follow it strictly.

---

# 🔍 **4. Anti‑Patterns (Agents Must Avoid)**

### 🚫 **4.1 Do not infer file contents**  
Always call `read_file()`.

### 🚫 **4.2 Do not assume schema structure**  
Always call `get_schema()`.

### 🚫 **4.3 Do not invent lore or metaphysics**  
Always reference `lore_core.md` and `A_appendix.md`.

### 🚫 **4.4 Do not rely on memory of previous tool calls**  
Always re‑query when needed.

### 🚫 **4.5 Do not treat search results as complete context**  
Search is a locator, not a source of truth.

---

# 📘 **5. Example Workflows**

## **5.1 Retrieve a module’s responsibilities**
1. `list_files()`  
2. `get_module_purpose("monsterseed")`  
3. Use contents to guide generation or refactoring  

---

## **5.2 Validate a YAML structure**
1. `get_schema("seed_type")`  
2. Compare user‑provided YAML to schema  
3. Report mismatches or generate corrected YAML  

---

## **5.3 Answer a lore question**
1. `search("Lumen Storm")`  
2. Identify file(s)  
3. `read_file()` for full context  
4. Respond using canonical definitions  

---

# 🧱 **6. Agent Behavior Expectations**

Agents interacting with this tool must:

- cite which file(s) they used  
- avoid mixing canonical and non‑canonical information  
- prefer explicit retrieval over inference  
- maintain consistency across all generated content  
- request clarification when documentation is insufficient  

---

# 🎉 **7. Summary**

This guide ensures all agents:

- use the IntelliHub consistently  
- retrieve canonical information correctly  
- avoid hallucination  
- maintain architectural and lore integrity  
- collaborate predictably within the MonTamerGens ecosystem  

The IntelliHub MCP Tool is the backbone of agent‑driven development.  
Use it with precision.

---
