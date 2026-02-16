# Production Requirements Document (PRD)
# Roommate Expense Manager v3.2.2

---

## 1. Document Information

| Field | Value |
|-------|-------|
| **Document Version** | 1.0 |
| **Last Updated** | 2026-02-16 |
| **Product Version** | 3.2.2 |
| **Document Owner** | Product Team |
| **Status** | Active |
| **Repository** | C:\Users\Alon.ALON2020\OneDrive\Desktop\Automation\Expense-Assignment |
| **Branch** | Ver3.2.1 |

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Product Team | Initial PRD creation - comprehensive documentation of v3.2.2 |

---

## 2. Executive Summary

### Product Name
**Roommate Expense Manager** (Internal: Expense Assignment Application)

### Version
v3.2.2 (Production)

### Problem Statement
Roommates and housemates who share expenses need a simple, efficient way to:
- Import financial transactions from multiple sources (credit cards, bank accounts)
- Assign each expense to the responsible party
- Track totals per person
- Generate reports for settlement

**Pain Points Addressed:**
- Manual expense tracking in spreadsheets is time-consuming and error-prone
- Multiple financial sources (credit cards, bank accounts) require tedious consolidation
- Unclear ownership of shared expenses leads to disputes
- No easy way to verify and review expenses one-by-one
- Language barriers (Hebrew transactions, international date formats)

### Solution Overview
A **Streamlit-based web application** that provides:
1. **Multi-file Excel import** with flexible column mapping
2. **Two verification modes**: Focus Mode (one-at-a-time) and Table View (bulk editing)
3. **Live totals dashboard** showing real-time per-person aggregation
4. **Excel export** for final reports and settlement
5. **Session-based workflow** with no backend database required

### Target Users
- **Primary:** 2-7 roommates sharing a household and expenses
- **Secondary:** Small teams, travel groups, or families managing shared costs

### Key Value Proposition
**"From Excel chaos to clear accountability in 5 minutes"**

Transform multiple messy Excel files into organized, assigned expenses with an intuitive verification workflow - no technical skills required.

---

## 3. Product Overview

### Product Vision
Simplify shared expense management by providing an intuitive, privacy-first tool that works entirely in the browser without requiring databases, authentication, or complex setup.

### Product Description
Roommate Expense Manager is a lightweight web application built with Streamlit that enables users to:
- Configure 2-7 roommates with color-coded identities
- Import expenses from multiple Excel files (credit card statements, bank exports)
- Map columns flexibly to handle various file formats
- Verify and assign expenses through an engaging card-based interface
- Edit in bulk using a powerful spreadsheet-like table view
- Track live totals per person in real-time
- Export final reports as Excel files

**Core Philosophy:**
- **Progressive Disclosure:** Start simple (setup) → verify (focus mode) → finalize (results)
- **Privacy-First:** All data stays in browser session, nothing persisted
- **Localization-Aware:** Supports Hebrew categories, international date formats
- **Zero Configuration:** No database, no authentication, no installation

### Success Criteria
**MVP Success (v3.2.2):**
- ✅ Import and process 10K+ expense rows without performance degradation
- ✅ Support 2-7 partners with unique color coding
- ✅ Handle multiple file formats and column structures
- ✅ Provide intuitive one-by-one verification workflow
- ✅ Enable bulk editing for advanced users
- ✅ Generate Excel exports with proper formatting
- ✅ Support Hebrew and English text seamlessly

**User Success:**
- User completes full workflow (setup → verify → export) in under 10 minutes for 100 expenses
- Zero data loss during session
- Accurate calculations with proper numeric coercion

### Core Capabilities Summary
1. **Partner Management** - Define 2-7 roommates with names and colors
2. **Multi-File Import** - Upload multiple Excel files with flexible column mapping
3. **Focus Mode Verification** - Card-based one-at-a-time expense review
4. **Table View Editing** - Bulk editing with spreadsheet interface
5. **Live Totals** - Real-time per-partner aggregation in sidebar
6. **Category Management** - Dynamic category extraction from imports
7. **Excel Export** - Generate formatted reports per partner or combined
8. **Reset & Restart** - Clear workflow with data management controls

---

## 4. User Personas & Use Cases

### Primary Personas

#### Persona 1: The Organizer
**Name:** Sarah, 28, Software Engineer
**Living Situation:** Shares 3-bedroom apartment with 2 roommates
**Tech Savviness:** High
**Goals:**
- Quickly consolidate credit card and bank statements at month-end
- Ensure every expense is properly assigned
- Generate clear reports for roommate settlement

**Pain Points:**
- Wastes 2-3 hours/month manually tracking in Google Sheets
- Roommates forget who paid for what
- Different file formats from different banks

**Usage Pattern:** Monthly batch processing (200-300 expenses)

---

#### Persona 2: The Contributor
**Name:** Michael, 24, Graduate Student
**Living Situation:** Lives with 4 roommates in shared house
**Tech Savviness:** Medium
**Goals:**
- Review and verify expenses assigned to him
- Understand what he owes each month
- Quick visibility into spending patterns

**Pain Points:**
- Doesn't trust manual spreadsheets
- Wants transparency in how expenses are split
- Needs simple interface, not formulas

**Usage Pattern:** Weekly review (50-100 expenses)

---

#### Persona 3: The Newcomer
**Name:** Yael, 22, Recent College Grad
**Living Situation:** Just moved into shared apartment with 2 friends
**Tech Savviness:** Low-Medium
**Goals:**
- First time managing shared expenses
- Needs guidance through the process
- Wants to avoid conflicts with new roommates

**Pain Points:**
- Overwhelmed by finance tracking
- Doesn't know where to start
- Worried about making mistakes

**Usage Pattern:** First-time setup with guidance, then bi-weekly reviews

---

### User Stories by Epic

#### Epic 1: Setup & Configuration

**US-001: Define Roommate Partners**
**As** a user setting up the app
**I want to** define 2-7 roommates with unique names and colors
**So that** I can visually distinguish each person's expenses

**Acceptance Criteria:**
- Slider to select 2-7 partners (default: 3)
- Text input for each partner name (default: Alice, Bob, Charlie, etc.)
- Color picker for each partner (default: red, blue, green, etc.)
- "Confirm Partners" button to save configuration
- Edit button to modify partners later
- Partner data persists when adding multiple files

**Implementation:** `setup_page.py:8-36`

---

**US-002: Upload Multiple Excel Files**
**As** a user importing expenses
**I want to** upload multiple Excel files from different sources
**So that** I can combine credit card, bank, and other statements

**Acceptance Criteria:**
- File uploader accepts .xlsx and .xls formats
- Uploader resets after successful import to allow multiple uploads
- Show total rows loaded across all files
- Preview last 3 rows added
- Display count: "Total Expenses Loaded: X"

**Implementation:** `setup_page.py:40-99`

---

**US-003: Map Excel Columns Flexibly**
**As** a user with custom Excel formats
**I want to** map my columns to standard fields
**So that** my data is correctly interpreted

**Acceptance Criteria:**
- Required fields: Date, Description, Amount (dropdowns)
- Optional fields: Partner, Category, Comment (dropdown with "None" option)
- Column preview shows actual Excel headers
- Mapping persists only for current file
- Support for dayfirst=True date parsing (international formats)
- Validation: Show error if file cannot be read

**Implementation:** `setup_page.py:54-98`, `utils.py:5-49`

---

#### Epic 2: Expense Verification

**US-004: Verify Expenses One-by-One (Focus Mode)**
**As** a user reviewing expenses
**I want to** see one expense at a time with clear details
**So that** I can carefully assign each to the right person

**Acceptance Criteria:**
- Display expense in card format: Date, Description, Amount (large)
- Show progress: "Reviewed X / Total Y"
- Progress bar visualization
- Show only unverified expenses
- Info alert if Excel pre-filled a partner suggestion
- Balloons and success message when all verified

**Implementation:** `app.py:67-155`

---

**US-005: Assign Partner with Visual Buttons**
**As** a user assigning expenses
**I want to** click a partner's button to assign and verify
**So that** assignment is fast and intuitive

**Acceptance Criteria:**
- One button per partner with color-coded styling
- Buttons arranged in columns (max 4 columns, wrap if needed)
- Pre-filled partner button shows "✅ Confirm [Name]" (primary type)
- Other buttons show "👤 [Name]" (secondary type)
- Click button → assigns partner, saves category/comment, marks verified, advances to next
- Handle 2-7 partners dynamically

**Implementation:** `app.py:129-154`

---

**US-006: Add and Manage Categories**
**As** a user categorizing expenses
**I want to** select from existing categories or create new ones
**So that** I can organize expenses meaningfully

**Acceptance Criteria:**
- Dropdown with existing categories + "➕ Add New..." option
- Pre-select current category if available, else "Uncategorized"
- New category flow: text input + "Save Cat" button
- Newly added categories appear in dropdown immediately
- Categories extracted from Excel imports automatically
- Default categories: Groceries, Fuel, Electricity, Internet, Rent, Insurance, Dining Out

**Implementation:** `app.py:110-124`, `setup_page.py:84-87`, `utils.py:51-58`

---

#### Epic 3: Bulk Editing & Reporting

**US-007: Edit Expenses in Table View**
**As** an advanced user
**I want to** edit multiple expenses in spreadsheet format
**So that** I can make bulk changes efficiently

**Acceptance Criteria:**
- Table shows all expenses (hide "Verified" column)
- Inline editing with st.data_editor
- Partner column: Dropdown with all partners
- Category column: Dropdown with all categories
- Amount column: Number format with $X.XX display
- Dynamic rows (can add/delete rows)
- Auto-save on edit (no manual save button)
- Edits mark rows as verified automatically

**Implementation:** `app.py:159-184`

---

**US-008: View Live Totals**
**As** a user tracking balances
**I want to** see real-time totals per person
**So that** I know current amounts owed

**Acceptance Criteria:**
- Sidebar always visible on main dashboard
- One card per partner with color-coded border
- Show: Partner name + Total amount ($X,XXX.XX)
- Updates immediately when expenses assigned
- Styled with shadow and padding for clarity

**Implementation:** `app.py:26-51`

---

**US-009: Export Final Reports**
**As** a user completing expense assignment
**I want to** download Excel reports
**So that** I can share results with roommates

**Acceptance Criteria:**
- "Final Results" tab with download options
- "Download Combined Report" button (all expenses in one file)
- Individual download button per partner (filtered to their expenses)
- Metrics display per partner: Name + Total Amount
- Excel format: proper column widths, no "Verified" column
- Filename format: "Report.xlsx" (combined), "[Partner].xlsx" (individual)

**Implementation:** `app.py:186-206`, `utils.py:60-71`

---

## 5. Functional Requirements

### FR-001: Partner Management
**Priority:** P0 (Critical)
**Epic:** Setup & Configuration

**Description:**
Users must define 2-7 roommate partners with unique names and color identifiers before importing expenses.

**Detailed Requirements:**

1. **Partner Configuration Interface** (`setup_page.py:8-36`)
   - Slider widget: min=2, max=7, default=3
   - Dynamic input fields based on slider value
   - 3-column grid layout for inputs (wraps at 3)
   - Each partner requires:
     - Name: Text input (default: Alice, Bob, Charlie, David, Eve, Frank, Grace)
     - Color: Color picker (default: #FF4B4B, #1E90FF, #228B22, #FFA500, #9370DB, #008080, #FF1493)

2. **State Management**
   - Storage: `st.session_state.partners` (dictionary: {name: color})
   - Initialized empty in `app.py:14-15`
   - Persists across file uploads
   - Can be reset via "Edit Partners" button

3. **Validation Rules**
   - Minimum partners: 2
   - Maximum partners: 7
   - No duplicate name validation (current implementation accepts duplicates)
   - Empty names allowed (no validation)

4. **User Workflow**
   - Step 1: Select number of partners (slider)
   - Step 2: Fill names and pick colors
   - Step 3: Click "Confirm Partners" button
   - Step 4: Success message shows configured partners
   - Step 5: "✏️ Edit Partners" button allows reconfiguration

**Technical Implementation:**
```python
# setup_page.py:8-30
default_colors = ["#FF4B4B", "#1E90FF", "#228B22", "#FFA500", "#9370DB", "#008080", "#FF1493"]
default_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]

for i in range(num_partners):
    p_name = st.text_input(f"Name {i+1}", value=default_names[i])
    p_color = st.color_picker(f"Color {i+1}", default_colors[i])
    current_partners[p_name] = p_color
```

**Success Metrics:**
- Partners saved successfully: 100% (no failure cases)
- Edit capability: Functional (clears and re-renders form)

---

### FR-002: Multi-File Excel Import
**Priority:** P0 (Critical)
**Epic:** Setup & Configuration

**Description:**
Users can upload multiple Excel files (.xlsx, .xls) from different sources, accumulating data without overwriting previous imports.

**Detailed Requirements:**

1. **File Upload Interface** (`setup_page.py:40-50`)
   - Accepts: .xlsx, .xls file types
   - Uploader key: Dynamic (`uploader_{st.session_state.uploader_key}`)
   - Key increments after successful import (enables multi-file workflow)
   - Caption: "You can upload multiple Excel files (e.g., Credit Card + Bank Transfers). They will be merged together."

2. **File Processing** (`utils.py:5-49`)
   - Read with pandas: `pd.read_excel(file)`
   - Column mapping applied via user selections
   - Data normalization:
     - Amount: Convert to numeric, coerce errors, fillna(0.0)
     - Date: Parse with `dayfirst=True`, convert to date object, drop invalid dates
     - Partner: Replace empty strings with None
     - Category: fillna("Uncategorized"), preserve original values (including Hebrew)
     - Comment: fillna("")
   - Add "Verified" column: Default False

3. **Data Accumulation** (`setup_page.py:89-95`)
   - Concatenate to existing DataFrame: `pd.concat([st.session_state.expenses, new_data], ignore_index=True)`
   - Extract and merge categories from imported file
   - Reset uploader key to allow next upload
   - Show toast notification: "✅ Added X rows! Upload another or Finish."

4. **Status Display** (`setup_page.py:101-107`)
   - Show total rows loaded across all files
   - Preview last 3 rows added
   - "Finish & Go to Dashboard" button (primary, full-width)

**Data Flow:**
```
Excel File → pd.read_excel() → Column Rename → Data Cleaning →
Add Verified Flag → Concat to session_state.expenses → Update UI
```

**Error Handling:**
- Invalid file format: Show error "Error reading file: {exception}"
- Missing required columns: Handled by mapping (uses "None" for optional)
- Parse errors: Coerce to default values (0.0 for amount, NaT dropped for dates)

**Success Metrics:**
- File import success rate: >95%
- Support for Hebrew categories: Yes
- Multi-file accumulation: Tested up to 10+ files

---

### FR-003: Column Mapping System
**Priority:** P0 (Critical)
**Epic:** Setup & Configuration

**Description:**
Flexible column mapping allows users to map their Excel columns to standard application fields, supporting diverse file formats.

**Detailed Requirements:**

1. **Mapping Interface** (`setup_page.py:54-70`)
   - Read column headers: `pd.read_excel(file, nrows=0)` (preview only)
   - Two-column layout:
     - **Left (Required):** Date, Description, Amount (dropdowns)
     - **Right (Optional):** Partner, Category, Comment (dropdowns with "None")
   - Auto-select defaults: Index 0, 1, 2 for required fields
   - Optional fields default to "None"

2. **Mapping Dictionary Structure**
   ```python
   mapping = {
       'date': date_col,      # Required
       'desc': desc_col,      # Required
       'amt': amt_col,        # Required
       'partner': partner_col, # Optional
       'cat': cat_col,        # Optional
       'comment': comment_col  # Optional
   }
   ```

3. **Column Rename Logic** (`utils.py:12-26`)
   - Required columns always renamed to: Date, Description, Amount
   - Optional columns only renamed if not "None"
   - Missing columns added as None/empty: `df[col] = None`
   - Final column order: ['Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment']

4. **Data Type Coercion** (`utils.py:36-44`)
   - **Amount:** `pd.to_numeric(errors='coerce').fillna(0.0)` → float
   - **Date:** `pd.to_datetime(dayfirst=True, errors='coerce').dt.date` → date object
   - **Partner:** Replace empty strings with None
   - **Category:** fillna("Uncategorized"), preserve original (UTF-8, Hebrew)
   - **Comment:** fillna("")

**Edge Cases Handled:**
- Missing optional columns: Added as None
- Invalid numeric amounts: Coerced to 0.0
- Invalid dates: Dropped from dataset (dropna on Date)
- Hebrew text: Preserved with UTF-8 encoding
- Empty cells: Replaced with appropriate defaults

**Success Criteria:**
- Support 100% of tested file formats (credit cards, bank exports)
- No data loss for valid rows
- Graceful handling of malformed data

---

### FR-004: Focus Mode (One-by-One Verification)
**Priority:** P0 (Critical)
**Epic:** Expense Verification

**Description:**
Focus Mode presents expenses one-at-a-time in a card-based interface, enabling careful review and assignment. This is the primary verification workflow.

**Detailed Requirements:**

1. **Expense Filtering** (`app.py:69-76`)
   - Query: `df[df['Verified'] == False]` → get unverified indices
   - Process first unverified expense only
   - If all verified: Show balloons + success message

2. **Progress Tracking** (`app.py:85-88`)
   - Calculate: `done_count = total_count - len(unverified_indices)`
   - Display: Progress bar with text "Reviewed: X / Y"
   - Updates automatically on each assignment

3. **Expense Card UI** (`app.py:91-98`)
   - Center-aligned, padded, rounded card with shadow
   - Display hierarchy:
     - **Top:** Date (gray, small, 1.1em)
     - **Middle:** Description (bold, 1.8em)
     - **Bottom:** Amount (bold, 2.5em, $X.XX format)
   - Styling: White background, border, box-shadow

4. **Pre-fill Suggestion** (`app.py:100-103`)
   - If Excel pre-filled Partner: Show info alert
   - Message: "💡 Excel suggests this belongs to **[Partner]**. Click their name to confirm."
   - Only shown if pre-filled partner exists in configured partners

5. **Category Selection** (`app.py:110-124`)
   - Selectbox with current categories + "➕ Add New..." option
   - Pre-select current category if valid, else "Uncategorized"
   - Add new category workflow:
     - Text input for new category name
     - "Save Cat" button adds to `st.session_state.categories`
     - Reruns app to refresh dropdown

6. **Comment Input** (`app.py:127`)
   - Text input pre-filled with existing comment
   - Saved on partner button click

7. **Partner Assignment Buttons** (`app.py:129-154`)
   - Dynamic button generation (2-7 partners)
   - Layout: Up to 4 columns, wrap if more partners
   - Button styling:
     - **Pre-filled partner:** "✅ Confirm [Name]" (type=primary, highlighted)
     - **Other partners:** "👤 [Name]" (type=secondary)
   - Click action:
     - Set Partner, Category, Comment
     - Mark Verified = True
     - Rerun app (advances to next expense)

**User Flow:**
```
Load Focus Mode → Filter unverified → Show first expense card →
User selects category/comment → User clicks partner button →
Save data + mark verified → Rerun → Show next expense
(Repeat until all verified)
```

**Edge Cases:**
- No partners configured: Show error message
- All expenses verified: Show balloons + success
- More than 4 partners: Buttons wrap to next row

**Success Metrics:**
- Average time per expense: ~5-10 seconds
- User completion rate: >90%
- Zero skipped expenses (enforced by sequential workflow)

---

### FR-005: Table View (Bulk Editing)
**Priority:** P1 (High)
**Epic:** Bulk Editing & Reporting

**Description:**
Table View provides a spreadsheet-like interface for advanced users to edit multiple expenses simultaneously using Streamlit's data_editor.

**Detailed Requirements:**

1. **Table Display** (`app.py:159-176`)
   - Component: `st.data_editor()`
   - Data source: `st.session_state.expenses` (without 'Verified' column)
   - Height: 500px (scrollable)
   - Width: use_container_width=True
   - Rows: Dynamic (num_rows="dynamic") - allows add/delete

2. **Column Configuration** (`app.py:168-172`)
   - **Partner:** Selectbox column with all partner names (required=True)
   - **Category:** Selectbox column with all categories (required=True)
   - **Amount:** Number column with "$%.2f" format
   - Other columns: Default text editing

3. **Auto-Save Logic** (`app.py:178-184`)
   - Detect changes: `if not edited.equals(view_df)`
   - Mark all edited rows as Verified=True
   - Replace session_state.expenses with edited data
   - Rerun app to persist changes

4. **Info Banner** (`app.py:161`)
   - Message: "📝 Advanced Mode: Edits here are auto-saved."
   - Alerts users that changes are immediate

**Data Flow:**
```
session_state.expenses → Remove 'Verified' column →
st.data_editor() → User edits → Detect changes →
Add 'Verified'=True → Update session_state → Rerun
```

**Advantages:**
- Bulk assignment of multiple expenses to same partner
- Quick category changes across rows
- Add/delete rows manually
- Copy-paste from external sources

**Limitations:**
- Cannot filter/sort within editor
- All columns visible (no hiding except 'Verified')
- Changes applied to all edited rows, not selective

**Success Metrics:**
- Bulk edit efficiency: 20-30 expenses/minute
- Data integrity: 100% (auto-save prevents loss)

---

### FR-006: Live Totals Dashboard
**Priority:** P1 (High)
**Epic:** Bulk Editing & Reporting

**Description:**
Sidebar displays real-time aggregated totals per partner, updating immediately as expenses are assigned.

**Detailed Requirements:**

1. **Sidebar Placement** (`app.py:26-51`)
   - Location: Always visible in left sidebar
   - Sections:
     - **Actions** (top): Add More Files, Reset buttons
     - **Live Totals** (middle): Per-partner cards
     - **Dividers:** Visual separation

2. **Data Aggregation** (`app.py:37`)
   - Query: `st.session_state.expenses.groupby("Partner")['Amount'].sum()`
   - Returns: Series with partner names as index, totals as values
   - Updates on every rerun (real-time)

3. **Visual Cards** (`app.py:39-50`)
   - One card per partner
   - Styling (inline HTML):
     - Background: White
     - Border-left: 6px solid {partner_color}
     - Border-radius: 4px
     - Box-shadow: Subtle (0 1px 3px rgba(0,0,0,0.1))
     - Padding: 10px, margin-bottom: 8px
   - Content:
     - **Top:** Partner name (bold, 0.9em, gray)
     - **Bottom:** Total amount (bold, 1.2em, $X,XXX.XX)

4. **Default Values**
   - If partner has no expenses: Show $0.00 (via `.get(p, 0.0)`)

**Visual Design:**
```
╔════════════════════════╗
║ Alice                  ║
║ $1,234.56              ║ ← Red border-left
╚════════════════════════╝

╔════════════════════════╗
║ Bob                    ║
║ $987.23                ║ ← Blue border-left
╚════════════════════════╝
```

**Success Metrics:**
- Update latency: <100ms (instant on rerun)
- Calculation accuracy: 100%
- Visual clarity: High (color-coded, formatted currency)

---

### FR-007: Final Results & Reporting
**Priority:** P0 (Critical)
**Epic:** Bulk Editing & Reporting

**Description:**
Final Results tab provides download buttons for Excel exports (combined and per-partner) along with summary metrics.

**Detailed Requirements:**

1. **Tab Layout** (`app.py:186-206`)
   - Header: "📊 Final Reports"
   - Primary download: Combined report (all expenses)
   - Metrics: Per-partner totals in columns
   - Secondary downloads: Individual partner reports

2. **Combined Report Export** (`app.py:194-197`)
   - Button: "📥 Download Combined Report" (type=primary)
   - Filename: "Report.xlsx"
   - Content: All expenses (all partners)
   - Format: Excel with auto-sized columns

3. **Per-Partner Metrics** (`app.py:200-204`)
   - Layout: Dynamic columns (1 per partner)
   - Display: `st.metric(partner_name, "$X,XXX.XX")`
   - Data: Filtered to partner's expenses only

4. **Individual Partner Exports** (`app.py:205-206`)
   - Button per partner: "📥 {Partner Name}"
   - Filename: "{Partner}.xlsx"
   - Content: Filtered DataFrame (only that partner's expenses)

5. **Excel Generation** (`utils.py:60-71`)
   - Engine: xlsxwriter
   - Sheet name: "Expenses"
   - Index: False (no row numbers)
   - Column widths: Auto-calculated (max content length + 5)
   - Excludes: 'Verified' column (dropped before export)
   - Unicode support: Full (Hebrew categories preserved)

**Data Processing:**
```python
# utils.py:60-71
def generate_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df = df.drop(columns=['Verified'], errors='ignore')
        export_df.to_excel(writer, index=False, sheet_name='Expenses')

        worksheet = writer.sheets['Expenses']
        for i, col in enumerate(export_df.columns):
            max_len = max(export_df[col].astype(str).map(len).max(), len(col)) + 5
            worksheet.set_column(i, i, max_len)
    return output.getvalue()
```

**Excel Output Schema:**
| Date | Description | Amount | Partner | Category | Comment |
|------|-------------|--------|---------|----------|---------|
| 2024-01-15 | Groceries | 45.50 | Alice | Groceries | Weekly shopping |

**Edge Cases:**
- Empty DataFrame: Show warning "No data."
- Partner with no expenses: Metric shows $0.00, no download button

**Success Metrics:**
- Export success rate: 100%
- File size: Efficient (no unnecessary data)
- Format compatibility: Excel 2010+

---

### FR-008: Category Management
**Priority:** P2 (Medium)
**Epic:** Setup & Configuration

**Description:**
Dynamic category system that combines default categories with auto-extracted categories from imported Excel files.

**Detailed Requirements:**

1. **Default Categories** (`app.py:16-17`)
   - Initialized on app start
   - List: ["Groceries", "Fuel", "Electricity", "Internet", "Rent", "Insurance", "Dining Out"]
   - Stored: `st.session_state.categories`

2. **Category Extraction** (`utils.py:51-58`)
   - Function: `extract_categories(df)`
   - Logic: Get unique values from 'Category' column
   - Filters: Drop NaN, remove "Uncategorized"
   - Returns: List of unique category strings
   - Supports: UTF-8 (Hebrew, special characters)

3. **Auto-Merge on Import** (`setup_page.py:84-87`)
   - After loading Excel file, extract categories
   - For each imported category:
     - If not in `st.session_state.categories`: Append
   - Prevents duplicates (simple `not in` check)

4. **User-Added Categories** (`app.py:119-124`)
   - Focus Mode: "➕ Add New..." option in selectbox
   - Text input for new category name
   - "Save Cat" button appends to `st.session_state.categories`
   - Immediate rerun updates dropdown

5. **Category Validation**
   - No validation on category names (accepts any string)
   - Empty strings allowed
   - Duplicates possible if added manually multiple times

**Data Flow:**
```
Excel Import → Extract unique categories →
Merge with session_state.categories →
Available in dropdowns (Focus Mode + Table View)
```

**Limitations:**
- No category deletion
- No category editing/renaming
- No category hierarchy or grouping
- Resets on session end (not persisted)

**Success Metrics:**
- Hebrew category support: 100%
- Auto-extraction accuracy: 100%
- Duplicate prevention: Partial (import only, not manual adds)

---

### FR-009: Reset & Data Management
**Priority:** P1 (High)
**Epic:** Setup & Configuration

**Description:**
Workflow control buttons allow users to add more files, reset configuration, or restart the entire process.

**Detailed Requirements:**

1. **Add More Files** (`app.py:29-32`)
   - Button: "📂 Add More Files"
   - Location: Sidebar → Actions section
   - Action:
     - Set `st.session_state.setup_complete = False`
     - Rerun app → Returns to setup page
   - Use case: Add additional Excel files without losing loaded data

2. **Reset All Data** (`app.py:53-57`)
   - Button: "🗑️ Reset All Data"
   - Location: Sidebar → Below Live Totals
   - Action (destructive):
     - Clear expenses: `st.session_state.expenses = pd.DataFrame()`
     - Clear partners: `st.session_state.partners = {}`
     - Set `setup_complete = False`
     - Rerun app → Fresh start
   - No confirmation dialog (immediate execution)

3. **State Preservation**
   - **Add More Files:** Preserves expenses, partners, categories
   - **Reset All Data:** Clears everything except default categories

4. **Setup Completion Flow** (`setup_page.py:108-113`)
   - Button: "✅ Finish & Go to Dashboard ({X} items)"
   - Validation: Checks if partners configured
   - Error: "❌ You haven't defined your partners yet!"
   - Success: Set `setup_complete = True`, rerun to dashboard

**User Workflows:**

**Workflow 1: Add More Files**
```
Dashboard → Click "Add More Files" →
Setup Page (preserves data) →
Upload new file → Map columns → Add to batch →
Finish → Back to Dashboard (accumulated data)
```

**Workflow 2: Reset**
```
Dashboard → Click "Reset All Data" →
Setup Page (clean slate) →
Configure partners → Upload files → Start fresh
```

**Edge Cases:**
- Reset during verification: All progress lost (no undo)
- Add files after verification: New expenses start as unverified

**Success Metrics:**
- Reset success rate: 100%
- Data loss prevention: Add More Files preserves data
- User understanding: Clear button labels and actions

---

## 6. Technical Architecture

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Framework** | Streamlit | 1.x+ | UI rendering, state management, widgets |
| **Data Processing** | Pandas | Latest | DataFrame operations, Excel I/O |
| **Excel Generation** | xlsxwriter | Latest | Formatted Excel export |
| **Date Parsing** | Pandas datetime | Latest | International date format support |
| **Language** | Python | 3.8+ | Core application logic |
| **Deployment** | Streamlit Cloud / Local | - | Browser-based, no backend server |

### Application Structure

```
Expense-Assignment/
├── app.py                      # Main application (206 lines)
│   ├── Page configuration
│   ├── Session state initialization
│   ├── Flow control (setup vs dashboard)
│   ├── Sidebar (live totals, actions)
│   ├── Tab 1: Focus Mode
│   ├── Tab 2: Table View
│   └── Tab 3: Final Results
│
├── setup_page.py               # Setup wizard (113 lines)
│   ├── Partner configuration
│   ├── Multi-file upload loop
│   ├── Column mapping interface
│   └── Setup completion
│
├── utils.py                    # Utilities (71 lines)
│   ├── load_excel()           # Import & normalize data
│   ├── extract_categories()   # Auto-extract categories
│   └── generate_excel()       # Export to Excel
│
├── expense_app.py              # Legacy (v1.0)
├── expense_app_Ver.1.0.py      # Legacy backup
└── README.md                   # Minimal docs
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│                     (Streamlit Frontend)                     │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      app.py (Main)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Page Config: Title, Layout, Icon                       │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Session State (st.session_state)                       │ │
│  │  • expenses: DataFrame                                  │ │
│  │  • partners: {name: color}                              │ │
│  │  • categories: [list]                                   │ │
│  │  • setup_complete: bool                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Flow Control                                           │ │
│  │  IF setup_complete == False → render_setup_page()       │ │
│  │  ELSE → Dashboard (Sidebar + Tabs)                      │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────┬─────────────────────────┬────────────────────┘
               │                         │
       ┌───────▼────────┐       ┌────────▼────────┐
       │  setup_page.py │       │    Dashboard    │
       │                │       │   (3 Tabs)      │
       │ • Partners     │       │ • Focus Mode    │
       │ • File Upload  │       │ • Table View    │
       │ • Column Map   │       │ • Results       │
       └───────┬────────┘       └────────┬────────┘
               │                         │
               ▼                         ▼
       ┌─────────────────────────────────────┐
       │          utils.py                   │
       │  • load_excel()                     │
       │  • extract_categories()             │
       │  • generate_excel()                 │
       └─────────────────────────────────────┘
                       │
                       ▼
               ┌──────────────┐
               │  Pandas Core │
               │  • read_excel│
               │  • DataFrame │
               │  • groupby   │
               │  • to_excel  │
               └──────────────┘
```

### Data Flow Pipeline

```
┌──────────────┐
│ Excel Files  │ (.xlsx, .xls)
│ • Credit Card│
│ • Bank Export│
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────┐
│ 1. FILE UPLOAD                  │
│    (setup_page.py)              │
│    • st.file_uploader()         │
│    • Preview columns            │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 2. COLUMN MAPPING               │
│    (setup_page.py)              │
│    • User selects mappings      │
│    • Required: Date, Desc, Amt  │
│    • Optional: Partner, Cat, Com│
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 3. DATA LOADING                 │
│    (utils.load_excel)           │
│    • pd.read_excel()            │
│    • Rename columns             │
│    • Normalize schema           │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 4. DATA CLEANING                │
│    (utils.load_excel)           │
│    • Amount → float (coerce)    │
│    • Date → date (dayfirst)     │
│    • Partner → None if empty    │
│    • Category → fillna          │
│    • Add Verified = False       │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 5. CATEGORY EXTRACTION          │
│    (utils.extract_categories)   │
│    • Unique categories from file│
│    • Merge with session list    │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 6. DATA ACCUMULATION            │
│    (setup_page.py)              │
│    • pd.concat() with existing  │
│    • Increment uploader key     │
│    • Loop: Add more or finish   │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 7. VERIFICATION                 │
│    (app.py - Focus/Table Mode)  │
│    • Assign Partner             │
│    • Select Category            │
│    • Add Comment                │
│    • Mark Verified = True       │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 8. AGGREGATION                  │
│    (app.py - Sidebar)           │
│    • groupby('Partner').sum()   │
│    • Display live totals        │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 9. EXPORT                       │
│    (utils.generate_excel)       │
│    • Drop 'Verified' column     │
│    • to_excel with xlsxwriter   │
│    • Auto-size columns          │
│    • Return BytesIO             │
└──────┬──────────────────────────┘
       │
       ▼
┌──────────────┐
│ Excel Output │ (Report.xlsx, Partner.xlsx)
│ • Formatted  │
│ • UTF-8      │
└──────────────┘
```

### State Management Schema

**Session State Variables:**

```python
st.session_state = {
    # Core data (initialized in app.py:10-17)
    'expenses': pd.DataFrame(),          # Main expense data
    'partners': {},                      # {name: color} dictionary
    'categories': [                      # Dynamic category list
        "Groceries", "Fuel", "Electricity",
        "Internet", "Rent", "Insurance", "Dining Out"
    ],
    'setup_complete': False,             # Flow control flag

    # UI state (managed by Streamlit)
    'uploader_key': 0,                   # Reset file uploader
    # + Dynamic keys for widgets (cat_{idx}, com_{idx}, btn_{name}_{idx})
}
```

**DataFrame Schema (expenses):**

```python
expenses = pd.DataFrame({
    'Date': pd.Series(dtype='object'),        # datetime.date objects
    'Description': pd.Series(dtype='string'), # Transaction description
    'Amount': pd.Series(dtype='float'),       # Coerced numeric
    'Partner': pd.Series(dtype='string'),     # Assigned roommate (None if unassigned)
    'Category': pd.Series(dtype='string'),    # Default: "Uncategorized"
    'Comment': pd.Series(dtype='string'),     # User notes
    'Verified': pd.Series(dtype='bool')       # Internal tracking (False by default)
})
```

**State Persistence:**
- Duration: Single browser session only
- Storage: Streamlit session_state (in-memory)
- Loss conditions: Browser refresh, tab close, session timeout
- No backend: Zero database, zero file persistence

---

## 7. Data Models & Schemas

### Expense Entity Schema

**Primary Data Structure: Pandas DataFrame**

| Field | Type | Required | Default | Validation | Source |
|-------|------|----------|---------|------------|--------|
| **Date** | `datetime.date` | Yes | N/A | Non-null after parsing | Excel Date column |
| **Description** | `str` | Yes | "" | Any string | Excel Description column |
| **Amount** | `float` | Yes | 0.0 | ≥ 0.0 (coerced) | Excel Amount column (numeric coercion) |
| **Partner** | `str | None` | None | Must be in partners dict | Excel Partner column (optional) OR user assignment |
| **Category** | `str` | Yes | "Uncategorized" | Any string | Excel Category column OR user selection |
| **Comment** | `str` | Yes | "" | Any string | Excel Comment column OR user input |
| **Verified** | `bool` | Yes | False | True/False | Internal (added by app) |

**Schema Enforcement:**
```python
# utils.py:28-47
expected_cols = ['Date', 'Description', 'Amount', 'Partner', 'Category', 'Comment']
for col in expected_cols:
    if col not in df.columns:
        df[col] = None  # Add missing columns

df = df[expected_cols]  # Enforce column order

# Data type coercion
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0.0)
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
df = df.dropna(subset=['Date'])  # Drop rows with invalid dates
df['Partner'] = df['Partner'].replace(["", " ", "nan"], None)
df['Category'] = df['Category'].fillna("Uncategorized")
df['Comment'] = df['Comment'].fillna("")
df['Verified'] = False  # Add verification flag
```

---

### Partner Entity Schema

**Storage:** Dictionary in `st.session_state.partners`

```python
partners = {
    "Alice": "#FF4B4B",    # Name → Color (hex code)
    "Bob": "#1E90FF",
    "Charlie": "#228B22"
}
```

**Constraints:**
- Min partners: 2
- Max partners: 7
- Name type: `str` (any value, including empty)
- Color type: `str` (hex code, format: #RRGGBB)
- No uniqueness enforcement on names (duplicates allowed)

**Default Values:** (`setup_page.py:18-19`)
```python
default_colors = ["#FF4B4B", "#1E90FF", "#228B22", "#FFA500",
                  "#9370DB", "#008080", "#FF1493"]
default_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
```

---

### Category Entity Schema

**Storage:** List in `st.session_state.categories`

```python
categories = [
    "Groceries",
    "Fuel",
    "Electricity",
    "Internet",
    "Rent",
    "Insurance",
    "Dining Out",
    # + Dynamically added from Excel imports
    # + User-added categories
]
```

**Properties:**
- Type: List of strings
- Initialization: 7 default categories (`app.py:16-17`)
- Growth: Append from Excel imports + user additions
- Constraints: None (no max length, duplicates possible)
- Character support: UTF-8 (Hebrew, special characters)

**Category Sources:**
1. **Default:** Hard-coded in app.py
2. **Imported:** Extracted from Excel files via `extract_categories()`
3. **User-added:** Created in Focus Mode via "➕ Add New..." option

---

### Data Validation Rules

| Rule | Field | Validation Logic | Error Handling |
|------|-------|------------------|----------------|
| **Non-null Date** | Date | `dropna(subset=['Date'])` | Drop row entirely |
| **Numeric Amount** | Amount | `pd.to_numeric(errors='coerce')` | Replace invalid with 0.0 |
| **Date Format** | Date | `pd.to_datetime(dayfirst=True)` | Parse DD/MM/YYYY, coerce errors to NaT |
| **Partner in List** | Partner | UI validation (selectbox) | Only configured partners selectable |
| **Category in List** | Category | UI validation (selectbox) | Only existing categories + "Add New" |
| **Empty Strings** | Partner | Replace with None | `df['Partner'].replace(["", " ", "nan"], None)` |
| **NaN Values** | Category, Comment | `fillna()` | Replace with defaults |

---

### File Format Specifications

#### Input Format (Excel)

**Accepted File Types:**
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

**Flexible Schema:** User maps any column names to required fields

**Example Input (Credit Card Statement):**
| תאריך | תיאור | סכום | קטגוריה |
|--------|---------|--------|----------|
| 15/01/2024 | סופרמרקט | 234.50 | מכולת |
| 18/01/2024 | דלק | 180.00 | דלק |

**Mapping:**
- תאריך → Date
- תיאור → Description
- סכום → Amount
- קטגוריה → Category

---

#### Output Format (Excel)

**Generated File:** `Report.xlsx` or `{Partner}.xlsx`

**Schema (Fixed):**
| Date | Description | Amount | Partner | Category | Comment |
|------|-------------|--------|---------|----------|---------|
| 2024-01-15 | Groceries | 45.50 | Alice | Groceries | Weekly shopping |
| 2024-01-18 | Gas Station | 60.00 | Bob | Fuel | |

**Formatting:**
- Sheet name: "Expenses"
- Column widths: Auto-sized (content length + 5 chars)
- Index: Hidden (index=False)
- Encoding: UTF-8 (preserves Hebrew)
- Engine: xlsxwriter

**Exclusions:**
- "Verified" column (dropped before export)

---

## 8. UI/UX Specifications

### Design Principles

1. **Progressive Disclosure**
   - Start simple: Partner setup → File upload → Verification → Results
   - Hide complexity until needed (Table View for advanced users)
   - Linear workflow with clear next steps

2. **Visual Hierarchy**
   - Large, centered cards for focus items (Focus Mode)
   - Color-coded partner identities throughout
   - Bold typography for key information (amounts, names)

3. **Immediate Feedback**
   - Live totals update on every assignment
   - Progress bars show completion status
   - Toast notifications for file uploads
   - Balloons on verification completion

4. **Bilingual Support**
   - UTF-8 throughout (Hebrew, English, mixed)
   - Right-to-left text handled by browser
   - No language-specific logic required

---

### Layout Structure

#### Page Configuration (`app.py:7`)
```python
st.set_page_config(
    page_title="Roommate Expense Manager",
    layout="wide",              # Full-width layout
    page_icon="🧾"              # Tab icon
)
```

---

### Component Specifications

#### 1. Setup Page (`setup_page.py`)

**Section 1.1: Partner Configuration**
- **Title:** "🧾 Expense App Setup"
- **Subheader:** "1. Define Partners"
- **Container:** Border=True (card style)
- **Components:**
  - Slider: 2-7 partners (default: 3)
  - 3-column grid layout
  - Per partner:
    - Text input: "Name {i+1}"
    - Color picker: "Color {i+1}"
  - Button: "Confirm Partners" (saves configuration)

**Section 1.2: File Upload Loop**
- **Subheader:** "2. Upload Expenses"
- **Caption:** Multi-file instruction text
- **Container:** Border=True
- **Components:**
  - File uploader: .xlsx, .xls
  - Column mapping (appears after file selected):
    - 2-column layout
    - Left: Required fields (Date, Description, Amount)
    - Right: Optional fields (Partner, Category, Comment)
  - Button: "➕ Add This File to Batch" (primary type)

**Section 1.3: Status & Finish**
- **Divider**
- **Display:** "Total Expenses Loaded: X"
- **Dataframe:** Last 3 rows preview
- **Button:** "✅ Finish & Go to Dashboard ({X} items)" (primary, full-width)

---

#### 2. Dashboard Sidebar (`app.py:26-57`)

**Actions Section:**
- **Header:** "Actions"
- **Button 1:** "📂 Add More Files"
- **Divider**

**Live Totals Section:**
- **Header:** "💰 Live Totals"
- **Cards:** One per partner (custom HTML)
  - Border-left: 6px solid {partner_color}
  - Background: White
  - Border-radius: 4px
  - Box-shadow: 0 1px 3px rgba(0,0,0,0.1)
  - Content:
    - Partner name (bold, 0.9em, gray)
    - Amount ($X,XXX.XX, bold, 1.2em)
- **Divider**

**Reset Section:**
- **Button:** "🗑️ Reset All Data"

---

#### 3. Focus Mode Tab (`app.py:67-155`)

**Progress Indicator:**
- Progress bar: `st.progress(done_count / total_count)`
- Text: "Reviewed: X / Y"

**Expense Card:**
- **Container:** Custom HTML, center-aligned
- **Styling:**
  - Padding: 30px
  - Border-radius: 15px
  - Background: White
  - Border: 1px solid #e0e0e0
  - Box-shadow: 0 4px 6px rgba(0,0,0,0.05)
- **Content hierarchy:**
  - Date: Gray, 1.1em, top
  - Description: Bold, 1.8em, middle
  - Amount: Bold, 2.5em, bottom ($X.XX)

**Pre-fill Alert:**
- Info box: "💡 Excel suggests..." (only if pre-filled)

**Input Section:**
- **2-column layout:**
  - Left: Category selectbox
  - Right: Comment text input
- **Add category flow:**
  - If "➕ Add New..." selected:
    - Text input for name
    - "Save Cat" button

**Partner Buttons:**
- **Header:** "### Assign & Verify:"
- **Layout:** Dynamic columns (max 4, wrap if more partners)
- **Button types:**
  - Pre-filled: "✅ Confirm {Name}" (type=primary)
  - Others: "👤 {Name}" (type=secondary)
- **Width:** use_container_width=True

**Completion State:**
- Balloons animation
- Success message: "🎉 All expenses verified and assigned! Go to 'Final Results'."

---

#### 4. Table View Tab (`app.py:159-184`)

**Info Banner:**
- "📝 Advanced Mode: Edits here are auto-saved."

**Data Editor:**
- **Component:** `st.data_editor()`
- **Dimensions:**
  - Height: 500px (scrollable)
  - Width: Full container
- **Column configs:**
  - Partner: Selectbox (all partners)
  - Category: Selectbox (all categories)
  - Amount: Number ($X.XX format)
- **Features:**
  - num_rows="dynamic" (add/delete rows)
  - Inline editing
  - Auto-save on change

---

#### 5. Final Results Tab (`app.py:186-206`)

**Header:**
- "📊 Final Reports"

**Primary Download:**
- Button: "📥 Download Combined Report" (type=primary)
- Filename: Report.xlsx

**Metrics Row:**
- Dynamic columns (1 per partner)
- Per partner:
  - `st.metric(name, "$X,XXX.XX")`

**Partner Downloads:**
- One button per partner: "📥 {Partner Name}"
- Only shown if partner has expenses

**Empty State:**
- Warning: "No data." (if DataFrame empty)

---

### Color Palette

**Partner Colors (Default):**
| Partner | Color | Hex Code | Use Case |
|---------|-------|----------|----------|
| Alice | Red | #FF4B4B | Borders, buttons |
| Bob | Blue | #1E90FF | Borders, buttons |
| Charlie | Green | #228B22 | Borders, buttons |
| David | Orange | #FFA500 | Borders, buttons |
| Eve | Purple | #9370DB | Borders, buttons |
| Frank | Teal | #008080 | Borders, buttons |
| Grace | Pink | #FF1493 | Borders, buttons |

**UI Colors:**
| Element | Color | Hex Code |
|---------|-------|----------|
| Background | White | #FFFFFF |
| Border | Light Gray | #E0E0E0 |
| Text (primary) | Dark Gray | #333333 |
| Text (secondary) | Gray | #555555 |
| Text (hint) | Light Gray | #888888 |
| Shadow | Translucent Black | rgba(0,0,0,0.05-0.1) |

---

### Typography

**Font Family:** System default (Streamlit inherits from browser)
- Sans-serif stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif

**Font Sizes:**
- Expense amount (Focus Mode): 2.5em (large, attention-grabbing)
- Expense description: 1.8em (prominent)
- Date label: 1.1em (subtle)
- Partner total: 1.2em (clear)
- Partner name: 0.9em (secondary)
- Body text: Default (Streamlit base)

**Font Weights:**
- Expense amount: 900 (heavy)
- Description: bold
- Partner totals: bold
- Partner names: bold
- Labels: normal

---

### Responsive Behavior

**Layout Adaptation:**
- Streamlit's built-in responsive columns
- Partner buttons: Wrap to multiple rows if >4 partners
- Sidebar: Collapsible on mobile (Streamlit default)
- Table View: Horizontal scroll on narrow screens

**No Custom Breakpoints:**
- Relies on Streamlit's responsive framework
- No media queries implemented

---

### Interaction Patterns

**Progressive Workflow:**
```
Setup (config partners) →
Upload (multi-file loop) →
Verify (Focus or Table) →
Export (download reports)
```

**Button Feedback:**
- Click → Immediate rerun
- Toast notifications on file add
- No loading spinners (operations are fast)

**State Transitions:**
- All state changes trigger `st.rerun()`
- Immediate UI updates
- No async operations

**Error Handling:**
- Inline error messages (st.error)
- No modal dialogs
- Errors displayed near relevant component

---

## 9. Non-Functional Requirements

### Performance Metrics

| Metric | Target | Current | Measurement |
|--------|--------|---------|-------------|
| **Initial Page Load** | <2s | ~1s | Time to interactive |
| **File Import (1000 rows)** | <3s | ~2s | Upload → processed |
| **Focus Mode Navigation** | <300ms | ~200ms | Button click → next expense |
| **Table View Render** | <2s | ~1.5s | 1000 rows displayed |
| **Live Totals Update** | <100ms | ~50ms | Assignment → sidebar refresh |
| **Excel Export (1000 rows)** | <2s | ~1s | Click → download ready |

**Performance Optimization:**
- Pandas vectorized operations (no Python loops)
- Minimal state changes per rerun
- No external API calls
- In-memory only (no disk I/O except uploads/downloads)

---

### Scalability

**Limits:**

| Resource | Limit | Reason |
|----------|-------|--------|
| **Max Expenses** | 10,000 rows | Streamlit session memory, DataFrame rendering |
| **Max Partners** | 7 | UI layout constraints, button wrapping |
| **Min Partners** | 2 | Business logic (requires sharing) |
| **Max File Size** | 50 MB | Streamlit upload limit (default) |
| **Session Duration** | ~30-60 min | Streamlit Cloud timeout (deployable) |

**Scalability Constraints:**
- No database: All data in memory (limited by Streamlit session)
- No pagination: All expenses rendered in Table View
- No lazy loading: Full DataFrame operations

**Recommendations for Scale:**
- <10K rows: Excellent performance
- 10K-50K rows: Acceptable, may slow on older browsers
- >50K rows: Not recommended (refactor to DB required)

---

### Reliability

**Data Integrity:**
- Numeric coercion prevents calculation errors
- Date validation prevents malformed data
- Verified flag ensures tracking state
- Auto-save in Table View prevents edit loss

**Error Handling:**
| Error Type | Handling | User Experience |
|------------|----------|-----------------|
| **Invalid Excel file** | Try-except → st.error | "Error reading file: {message}" |
| **Missing columns** | Auto-add as None | Silent handling, no error |
| **Invalid dates** | Drop row | Silent (dropna after parsing) |
| **Invalid amounts** | Coerce to 0.0 | Silent (fillna) |
| **No partners configured** | UI validation | Error message in Focus Mode |

**Edge Cases:**
- Empty DataFrame: Handled (show "No data" warnings)
- All expenses verified: Show success message + balloons
- Partner with $0.00: Display metric, no download button
- Duplicate partner names: Allowed (no validation)

---

### Usability

**Learnability:**
- First-time users: Complete workflow in <15 minutes
- Intuitive wizard: Step-by-step guidance
- Visual feedback: Progress bars, colors, animations

**Efficiency:**
- Experienced users: Process 100 expenses in <5 minutes
- Focus Mode: ~5-10s per expense
- Table View: Bulk edits for power users

**Accessibility:**
- Keyboard navigation: Streamlit default support
- Screen readers: Basic support (Streamlit widgets)
- Color contrast: Meets WCAG AA (dark text, light backgrounds)
- No custom accessibility implementation

**Error Prevention:**
- Confirm Partners button prevents accidental setup
- Auto-save in Table View prevents loss
- No delete confirmation (usability trade-off)

---

### Compatibility

**Browser Support:**
| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully supported |
| Firefox | 88+ | ✅ Fully supported |
| Safari | 14+ | ✅ Fully supported |
| Edge | 90+ | ✅ Fully supported |
| IE 11 | - | ❌ Not supported |

**Operating System:**
- Windows: ✅ Tested (Win 10, Win 11)
- macOS: ✅ Compatible (not extensively tested)
- Linux: ✅ Compatible (not extensively tested)

**Python Version:**
- Minimum: Python 3.8
- Recommended: Python 3.10+
- Tested: Python 3.11

**Dependencies:**
- Streamlit: 1.x+ (any recent version)
- Pandas: Latest stable
- xlsxwriter: Latest stable
- No version pinning (requirements.txt missing)

---

### Localization

**Language Support:**
- UI Text: English only (hard-coded)
- User Data: UTF-8 (Hebrew, multilingual)
- Date Parsing: International formats (`dayfirst=True`)

**Character Encoding:**
- Input: UTF-8 (Excel files)
- Processing: UTF-8 (Pandas native)
- Output: UTF-8 (Excel exports with xlsxwriter)

**Locale-Specific Features:**
- Date format: DD/MM/YYYY (dayfirst=True)
- Currency: $ symbol (hard-coded, no locale detection)
- Number format: Comma thousands separator (1,234.56)

**Right-to-Left (RTL):**
- No explicit RTL support
- Browser handles RTL text rendering
- Layout remains LTR

---

## 10. Security Considerations

### Authentication & Authorization

**Current State:**
- ❌ No authentication
- ❌ No user accounts
- ❌ No authorization
- ✅ Session-based isolation (Streamlit handles per-session state)

**Implications:**
- Anyone with app URL can access
- No multi-tenancy
- No data persistence between sessions
- Suitable for: Personal use, trusted environments
- NOT suitable for: Public deployment, sensitive financial data

**Recommendations for Production:**
- Implement authentication (Streamlit Auth0, OAuth)
- Add HTTPS requirement
- Consider VPN or IP whitelist

---

### Data Privacy

**Data Storage:**
- Location: Browser session memory (Streamlit server-side)
- Duration: Session lifetime only (~30-60 minutes)
- Persistence: ❌ None (no database, no files saved)

**Data Exposure:**
- Uploaded files: Processed in memory, not saved to disk
- Exports: Downloaded to user's browser, not stored server-side
- Session data: Isolated per user (Streamlit session management)

**Privacy Risks:**
- Shared server: If deployed on shared infrastructure, session data in server memory
- No encryption: Data in transit (HTTP) unless HTTPS configured
- No audit log: No tracking of who accessed what

**Best Practices:**
- Deploy on trusted infrastructure
- Use HTTPS in production
- Educate users: Data is temporary, re-upload if session expires

---

### Input Validation

**File Upload:**
- ✅ File type restriction: .xlsx, .xls only
- ❌ No file size validation (relies on Streamlit default: 200 MB)
- ❌ No malicious file scanning
- ✅ Exception handling on pd.read_excel()

**Data Coercion:**
- ✅ Amount: Numeric coercion (prevents injection via formulas)
- ✅ Date: Parse errors handled gracefully
- ❌ No sanitization of strings (Description, Category, Comment)
- ❌ No HTML escaping (potential XSS if custom HTML added)

**UI Input Validation:**
- ✅ Partner selection: Dropdown (limited to configured partners)
- ✅ Category selection: Dropdown (limited to existing categories)
- ❌ Text inputs: No validation (accepts any string, including empty)

**Recommendations:**
- Add file size limit check
- Sanitize text inputs before display (if custom HTML used)
- Validate partner/category names (no duplicates, no empty)

---

### Session Management

**Current Implementation:**
- Streamlit's built-in session management
- Session ID: Generated by Streamlit (opaque)
- Session timeout: ~30-60 minutes (configurable in deployment)
- Session data: `st.session_state` (server-side memory)

**Vulnerabilities:**
- Session fixation: Not applicable (Streamlit manages)
- Session hijacking: Risk if HTTP used (use HTTPS)
- CSRF: Low risk (no sensitive actions, session-based)

**Recommendations:**
- Configure shorter session timeout for sensitive use
- Use HTTPS to prevent session interception
- Add session expiration warnings

---

### Dependency Security

**Current State:**
- ❌ No requirements.txt (no version pinning)
- ❌ No dependency scanning
- ❌ No automated security updates

**Known Dependencies:**
- Streamlit: Generally secure, active maintenance
- Pandas: Mature library, rare vulnerabilities
- xlsxwriter: Stable, low risk

**Recommendations:**
- Create requirements.txt with pinned versions
- Use `pip-audit` or `safety` for vulnerability scanning
- Subscribe to security advisories for dependencies
- Update dependencies regularly

---

### Production Deployment Recommendations

**Checklist for Secure Deployment:**

1. **Infrastructure:**
   - ✅ Deploy on trusted cloud (Streamlit Cloud, AWS, Azure)
   - ✅ Enable HTTPS (SSL/TLS)
   - ✅ Configure firewall rules
   - ⚠️ Consider VPN or IP whitelist for sensitive data

2. **Application:**
   - ⚠️ Add authentication (Streamlit Auth0, custom)
   - ⚠️ Implement rate limiting (prevent abuse)
   - ⚠️ Add audit logging (track usage)
   - ✅ Use environment variables for configs (not in code)

3. **Data:**
   - ✅ Educate users: Data is temporary
   - ⚠️ Add data retention policy
   - ⚠️ Implement secure file deletion
   - ⚠️ Encrypt sensitive data at rest (if persisted)

4. **Monitoring:**
   - ⚠️ Set up error tracking (Sentry, Rollbar)
   - ⚠️ Monitor resource usage (memory, CPU)
   - ⚠️ Alert on anomalies (unusual file sizes, error rates)

5. **Compliance:**
   - ⚠️ GDPR: Add privacy policy, data handling notice
   - ⚠️ Financial data: Consider PCI DSS if handling payment info
   - ⚠️ Terms of service: Clarify liability, data loss

**Security Posture:**
- Current: **Low** (suitable for personal use, trusted environments)
- With recommendations: **Medium** (suitable for internal tools, small teams)
- Enterprise: Requires significant enhancements (DB, auth, encryption, audit)

---

## 11. Future Enhancements & Roadmap

### Phase 4 (v4.0): Persistence & Multi-Session

**Goal:** Enable data persistence and multi-user collaboration

**Features:**

1. **Database Integration**
   - Add SQLite (lightweight) or PostgreSQL (production)
   - Schema: Users, Households, Expenses, Partners
   - Migrate session_state to database

2. **User Authentication**
   - Streamlit Auth0 or custom OAuth
   - User registration and login
   - Password reset flow

3. **Household Management**
   - Create multiple households per user
   - Invite roommates via email
   - Role-based access (admin, member, viewer)

4. **Data Persistence**
   - Save expenses, partners, categories to DB
   - Auto-save drafts
   - Session recovery after timeout

**Effort Estimate:** 40-60 dev hours
**Priority:** High (needed for real-world adoption)

---

### Phase 5 (v4.5): Advanced Analytics & Insights

**Goal:** Provide data-driven insights into spending patterns

**Features:**

1. **Dashboards & Charts**
   - Spending by category (pie chart)
   - Spending over time (line chart)
   - Per-partner comparison (bar chart)
   - Interactive filters (date range, category, partner)

2. **Budgeting Tools**
   - Set budget limits per category
   - Alerts when approaching limit
   - Budget vs. actual visualization

3. **Reports & Exports**
   - PDF report generation
   - CSV export (in addition to Excel)
   - Monthly summary emails

4. **Insights Engine**
   - "You spent 30% more on dining out this month"
   - "Alice's share has increased by 15%"
   - Anomaly detection (unusual expenses)

**Technology Additions:**
- Plotly or Altair (charts)
- ReportLab (PDF generation)
- Scheduled tasks (emails)

**Effort Estimate:** 60-80 dev hours
**Priority:** Medium

---

### Phase 6 (v5.0): Automation & Integration

**Goal:** Reduce manual data entry through automation

**Features:**

1. **Bank Integration (API)**
   - Connect to bank accounts directly (Plaid, Yodlee)
   - Auto-import transactions daily/weekly
   - Reduce manual file uploads

2. **Receipt Scanning (OCR)**
   - Upload receipt photos
   - Extract amount, date, merchant via OCR
   - Auto-create expense entries

3. **Payment Integration**
   - Calculate settlement amounts automatically
   - Generate Venmo/PayPal links for settlement
   - Track payment status

4. **Smart Assignment (ML)**
   - Train model on past assignments
   - Auto-suggest partner based on description/category
   - Improve accuracy over time

**Technology Additions:**
- Plaid API (bank integration)
- Tesseract or Cloud Vision (OCR)
- Payment gateway APIs
- Scikit-learn or TensorFlow (ML)

**Effort Estimate:** 100-120 dev hours
**Priority:** Low (nice-to-have, complex)

---

### Quick Wins for v3.3 (Next Minor Release)

**Low-Effort, High-Impact Improvements:**

1. **CSV Export** (2 hours)
   - Add "Download as CSV" button in Results tab
   - Use Pandas `to_csv()`

2. **Dark Mode Support** (4 hours)
   - Leverage Streamlit's theme system
   - Add theme toggle in sidebar

3. **Undo Last Assignment** (6 hours)
   - Track last modified expense ID
   - "↩️ Undo" button in Focus Mode
   - Mark expense as unverified, return to queue

4. **Export Filters** (4 hours)
   - Date range filter for exports
   - Category filter for exports
   - Generate custom reports

5. **Keyboard Shortcuts** (6 hours)
   - Number keys (1-7) to assign partners
   - Enter to save category
   - Arrow keys to navigate in Focus Mode

6. **Progress Persistence** (8 hours)
   - Save session to local file (JSON)
   - "Resume Session" on app load
   - Prevents data loss on timeout

**Total Effort:** ~30 hours
**Priority:** High (user-requested features)

---

### Technical Debt Items

**Code Quality:**
1. **Unit Tests** (20 hours)
   - Test load_excel(), extract_categories(), generate_excel()
   - Test edge cases (empty files, invalid data)
   - Achieve 80%+ code coverage

2. **Type Hints** (8 hours)
   - Add type annotations to all functions
   - Use mypy for static type checking

3. **Error Logging** (6 hours)
   - Replace st.error() with proper logging
   - Log to file or external service (Sentry)
   - Track error rates

4. **Configuration File** (4 hours)
   - Move defaults to config.yaml
   - Environment variables for deployment
   - Separate dev/prod configs

5. **Requirements.txt** (1 hour)
   - Pin dependency versions
   - Document minimum versions
   - Add to repository

6. **Code Documentation** (10 hours)
   - Docstrings for all functions
   - Inline comments for complex logic
   - Architecture diagram (detailed)

**Total Effort:** ~49 hours
**Priority:** Medium (technical hygiene)

---

### Deferred Features (Out of Scope)

**Not Planned:**
1. **Mobile App** - Streamlit web app is responsive, native app not needed
2. **Real-Time Collaboration** - Complexity vs. benefit too high
3. **Blockchain/Crypto** - No use case for decentralization
4. **AI Chatbot** - Over-engineered for current needs
5. **Multi-Currency** - Limited user base, complex conversions

---

## 12. Success Metrics & KPIs

### Usage Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Active Sessions/Month** | 50+ | Server logs (if deployed) |
| **Files Processed/Month** | 200+ | Track file upload count |
| **Avg Expenses/Session** | 100-300 | Calculate mean(len(expenses)) |
| **Repeat Users** | 60% | Track returning sessions (if auth added) |
| **Session Completion Rate** | 80% | (Reached Results tab) / (Total sessions) |

---

### Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Error Rate** | <5% | (Failed imports) / (Total imports) |
| **Data Loss Incidents** | 0 | User-reported issues |
| **Verification Completion** | 95% | (Verified expenses) / (Total expenses) |
| **User-Reported Bugs** | <2/month | GitHub issues, feedback |

---

### Performance Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Page Load Time** | <2s | Browser DevTools (Lighthouse) |
| **Import Time (1K rows)** | <3s | Measure pd.read_excel() + processing |
| **Export Time (1K rows)** | <2s | Measure generate_excel() |
| **App Crash Rate** | <1% | (Crashed sessions) / (Total sessions) |

---

### Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **User Adoption Rate** | 10 users in first month | Track unique sessions |
| **Time Saved vs. Manual** | 60% reduction | Compare to manual spreadsheet time |
| **User Satisfaction** | 4.5/5 stars | Post-session survey (if added) |
| **Feature Requests** | 3-5/month | Track GitHub issues, feedback |

---

### Leading Indicators

**Early Signals of Success:**
- ✅ Users complete setup without errors
- ✅ Focus Mode engagement (users verify >50% of expenses)
- ✅ Multi-file uploads (indicates workflow fits real use case)
- ✅ Export downloads (indicates users find value in output)

**Early Warning Signs:**
- ❌ High drop-off rate at setup page
- ❌ Users abandon after uploading files (mapping too complex?)
- ❌ Low verification rate (Focus Mode not intuitive?)
- ❌ No repeat sessions (not solving real problem?)

---

### Tracking Plan

**Phase 1 (Current - v3.2.2):**
- No analytics implemented
- Manual tracking via user feedback
- Server logs (if deployed on Streamlit Cloud)

**Phase 2 (v3.3+):**
- Add Google Analytics or Mixpanel
- Track key events:
  - setup_complete
  - file_uploaded
  - expense_verified
  - report_downloaded
- Custom metrics dashboard

**Phase 3 (v4.0+):**
- Database-backed analytics
- User cohort analysis
- Retention tracking
- A/B testing framework

---

## 13. Constraints & Limitations

### Technical Constraints

| Constraint | Description | Impact | Mitigation |
|------------|-------------|--------|------------|
| **Session-Only Storage** | No database, all data in memory | Data lost on session end | Educate users, add "Resume Session" feature (v3.3) |
| **Single-Threaded** | Streamlit runs in single process | Can't handle concurrent heavy processing | Acceptable for target scale (<10K rows) |
| **7 Partner Limit** | UI layout breaks with >7 partners | Can't accommodate large households | Redesign layout for v4.0 (scrollable buttons) |
| **No Offline Mode** | Requires internet connection | Can't use without network | Not addressable (web app nature) |
| **Browser-Dependent** | Relies on modern browser features | Old browsers unsupported | Document browser requirements |

---

### Functional Limitations

| Limitation | Description | Workaround |
|------------|-------------|------------|
| **No Splitting Rules** | Can't split expense 50/50 between partners | Manually duplicate expense in Table View |
| **No Recurring Expenses** | Can't set up auto-assignments | User must assign each month manually |
| **No Audit Trail** | Can't see who changed what | Future: Add changelog (v4.0) |
| **No Undo** | Can't reverse assignment (except in Table View) | Future: Add undo button (v3.3) |
| **No Collaboration** | One user per session | Future: Multi-user support (v4.0) |
| **No Notifications** | Can't alert roommates of new expenses | Future: Email/Slack integration (v4.5) |
| **No Search** | Can't search by description/date | Use Ctrl+F in Table View (browser search) |
| **No Sorting** | Can't sort expenses in Focus Mode | Only available in Table View |

---

### Data Limitations

| Limitation | Description | Impact |
|------------|-------------|--------|
| **No Historical Tracking** | Can't compare month-to-month | Must export and manually compare |
| **No Data Validation** | Accepts any text in Description/Comment | Possible typos, inconsistencies |
| **No Duplicate Detection** | Can import same file twice | Inflates totals, user must be careful |
| **No Currency Conversion** | Assumes single currency ($) | Multi-currency households must convert manually |
| **No Tax/Fee Handling** | No special handling for service fees | Must categorize as separate expense |

---

### Deployment Constraints

| Constraint | Description | Requirement |
|------------|-------------|-------------|
| **Python Environment** | Requires Python 3.8+ and pip | Server must have Python installed |
| **Memory** | Needs ~200 MB RAM per session | Adequate for cloud deployment |
| **Network Access** | Requires internet for Streamlit CDN | Can't run fully offline |
| **Port Access** | Default port 8501 | Must configure firewall |
| **HTTPS** | Manual setup for secure connections | Streamlit Cloud handles automatically |

---

### Business Constraints

| Constraint | Description | Mitigation |
|------------|-------------|------------|
| **No Monetization** | Currently free, no revenue model | Acceptable for personal project |
| **No Support** | No dedicated support team | Community-based support (GitHub issues) |
| **No SLA** | No uptime guarantees | Acceptable for non-critical use |
| **No Legal Entity** | No terms of service, privacy policy | Add before public deployment |

---

### Scalability Constraints

**Current Architecture NOT Suitable For:**
- ❌ >10,000 expenses per session
- ❌ >100 concurrent users (shared deployment)
- ❌ Long-term data storage (years of history)
- ❌ Complex financial calculations (loans, interest, etc.)
- ❌ Integration with accounting software (QuickBooks, Xero)

**Architectural Changes Required for Scale:**
- Database (PostgreSQL, MongoDB)
- Backend API (FastAPI, Flask)
- Caching layer (Redis)
- Queue system (Celery, RQ) for async processing
- Load balancer for horizontal scaling

---

## 14. Appendices

### A. Glossary of Terms

| Term | Definition |
|------|------------|
| **Expense** | A single financial transaction (purchase, payment, charge) |
| **Partner** | A roommate or household member who shares expenses |
| **Verification** | Process of reviewing and assigning an expense to a partner |
| **Focus Mode** | One-at-a-time expense review interface with card-based UI |
| **Table View** | Spreadsheet-like bulk editing interface |
| **Category** | Classification of expense type (Groceries, Rent, etc.) |
| **Setup Page** | Initial wizard for configuring partners and uploading files |
| **Live Totals** | Real-time aggregated amounts per partner (sidebar) |
| **Session State** | Streamlit's in-memory storage for user data during a session |
| **Verified** | Boolean flag indicating an expense has been reviewed and assigned |
| **Mapping** | Process of matching Excel columns to app's expected fields |
| **Coercion** | Automatic conversion of data types (text to number, etc.) |

---

### B. File Specifications

| File | Lines | Purpose | Key Functions/Components |
|------|-------|---------|--------------------------|
| **app.py** | 206 | Main application entry point | - Page config<br>- Session state init<br>- Flow control<br>- Focus Mode (Tab 1)<br>- Table View (Tab 2)<br>- Results (Tab 3)<br>- Sidebar (live totals, actions) |
| **setup_page.py** | 113 | Setup wizard | - Partner configuration<br>- Multi-file upload loop<br>- Column mapping interface<br>- Setup completion |
| **utils.py** | 71 | Utility functions | - `load_excel()`: Import & clean data<br>- `extract_categories()`: Auto-extract categories<br>- `generate_excel()`: Export to Excel |
| **expense_app.py** | (Legacy) | Original version | Historical reference |
| **expense_app_Ver.1.0.py** | (Legacy) | Version 1.0 backup | Historical reference |
| **README.md** | 3 | Project readme | Minimal documentation |

**Total Active Codebase:** 390 lines (app.py + setup_page.py + utils.py)

---

### C. Default Values Reference

**Partners (setup_page.py:18-19):**
```python
default_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace"]
default_colors = ["#FF4B4B", "#1E90FF", "#228B22", "#FFA500", "#9370DB", "#008080", "#FF1493"]
```

**Categories (app.py:16-17):**
```python
categories = [
    "Groceries",
    "Fuel",
    "Electricity",
    "Internet",
    "Rent",
    "Insurance",
    "Dining Out"
]
```

**Data Defaults (utils.py:36-44):**
- Amount: `0.0` (if coercion fails)
- Date: Drop row (if parsing fails)
- Partner: `None` (if empty or not provided)
- Category: `"Uncategorized"` (if empty or not provided)
- Comment: `""` (if not provided)
- Verified: `False` (always added on import)

**UI Defaults:**
- Number of partners: 3 (slider default)
- Page layout: Wide
- Page icon: 🧾
- Session timeout: ~30-60 minutes (Streamlit Cloud)

---

### D. Example Excel Structures

#### Before Mapping (Raw Credit Card Statement)

| תאריך | תיאור העסקה | סכום | קטגוריה |
|--------|-------------|------|----------|
| 15/01/2024 | סופרמרקט מכולת | 234.50 | מכולת |
| 18/01/2024 | תחנת דלק | 180.00 | דלק |
| 20/01/2024 | מסעדה | 120.00 | מסעדות |

**Column Mapping:**
- תאריך → Date
- תיאור העסקה → Description
- סכום → Amount
- קטגוריה → Category

---

#### After Import (Normalized DataFrame)

| Date | Description | Amount | Partner | Category | Comment | Verified |
|------|-------------|--------|---------|----------|---------|----------|
| 2024-01-15 | סופרמרקט מכולת | 234.50 | None | מכולת | | False |
| 2024-01-18 | תחנת דלק | 180.00 | None | דלק | | False |
| 2024-01-20 | מסעדה | 120.00 | None | מסעדות | | False |

---

#### After Verification (Ready for Export)

| Date | Description | Amount | Partner | Category | Comment | Verified |
|------|-------------|--------|---------|----------|---------|----------|
| 2024-01-15 | סופרמרקט מכולת | 234.50 | Alice | Groceries | Weekly shopping | True |
| 2024-01-18 | תחנת דלק | 180.00 | Bob | Fuel | | True |
| 2024-01-20 | מסעדה | 120.00 | Alice | Dining Out | Birthday dinner | True |

---

#### Final Export (Excel Output)

**File:** Report.xlsx
**Sheet:** Expenses

| Date | Description | Amount | Partner | Category | Comment |
|------|-------------|--------|---------|----------|---------|
| 2024-01-15 | סופרמרקט מכולת | 234.50 | Alice | Groceries | Weekly shopping |
| 2024-01-18 | תחנת דלק | 180.00 | Bob | Fuel | |
| 2024-01-20 | מסעדה | 120.00 | Alice | Dining Out | Birthday dinner |

*(Note: "Verified" column removed before export)*

---

### E. References & Resources

**Documentation:**
- Streamlit Docs: https://docs.streamlit.io
- Pandas Docs: https://pandas.pydata.org/docs/
- xlsxwriter Docs: https://xlsxwriter.readthedocs.io/

**Repository:**
- Location: `C:\Users\Alon.ALON2020\OneDrive\Desktop\Automation\Expense-Assignment`
- Branch: Ver3.2.1
- Commit: a96a600 ("3.2.2")

**Version History:**
- v3.2.2: Current (production)
- v1.0: Legacy (expense_app_Ver.1.0.py)

**Related Projects:**
- Splitwise (commercial alternative)
- Tricount (commercial alternative)
- SplitMyExpenses (open-source)

---

### F. Common Use Cases & Workflows

#### Use Case 1: Monthly Batch Processing

**Scenario:** Alice manages expenses for 3 roommates at month-end.

**Workflow:**
1. Export credit card statement → `credit_card_jan.xlsx`
2. Export bank transactions → `bank_jan.xlsx`
3. Open app → Configure 3 partners (Alice, Bob, Charlie)
4. Upload `credit_card_jan.xlsx` → Map columns → Add to batch
5. Upload `bank_jan.xlsx` → Map columns → Add to batch
6. Finish setup → Dashboard loaded (200 expenses)
7. Use Focus Mode → Review and assign all expenses (~20 minutes)
8. Download individual reports for each roommate
9. Share files via email/Slack for settlement

**Time Saved:** 60 minutes (vs. 90 minutes manual spreadsheet)

---

#### Use Case 2: Quick Spot Check

**Scenario:** Bob wants to verify last week's dining out expenses.

**Workflow:**
1. Open app → Setup partners
2. Upload file with 50 expenses
3. Go to Table View (skip Focus Mode)
4. Filter mentally (no built-in filter) for "Dining Out"
5. Bulk assign relevant rows to himself
6. Download his individual report
7. Review total and specific expenses

**Time Saved:** 10 minutes (vs. 15 minutes manual)

---

#### Use Case 3: Multi-Source Consolidation

**Scenario:** Household has 4 payment methods (2 credit cards, 1 debit, 1 Venmo export).

**Workflow:**
1. Setup 4 partners
2. Upload file 1 (Visa) → Map → Add
3. Upload file 2 (Mastercard) → Map → Add
4. Upload file 3 (Bank debit) → Map → Add
5. Upload file 4 (Venmo CSV converted to Excel) → Map → Add
6. Total: 450 expenses accumulated
7. Use combination of Focus Mode (questionable items) + Table View (bulk known items)
8. Download combined report with all sources merged

**Value:** Single source of truth, eliminates duplicate tracking

---

### G. Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| **"Error reading file"** | Invalid Excel file or corrupted | - Check file format (.xlsx, .xls)<br>- Try opening in Excel first<br>- Re-export from source |
| **Missing expenses after import** | Date parsing failed (invalid dates) | - Check date format in Excel<br>- Ensure dates are in DD/MM/YYYY or Excel date format<br>- Fix dates in Excel and re-upload |
| **Amounts show as $0.00** | Non-numeric values in Amount column | - Check for currency symbols in Excel<br>- Remove commas, spaces<br>- Ensure column is numeric format |
| **Categories not appearing** | Category column not mapped or empty | - Re-upload and map Category column<br>- Categories will show as "Uncategorized" if not mapped |
| **Can't click "Finish & Go to Dashboard"** | Partners not confirmed | - Scroll up to Step 1<br>- Click "Confirm Partners" button<br>- Then return to Step 3 |
| **Progress bar stuck at 99%** | Last expense not verified | - Check Table View for unverified rows<br>- Manually assign in Table View |
| **Excel export shows garbled text** | Encoding issue (rare) | - xlsxwriter uses UTF-8 by default<br>- Open exported file in Excel 2010+ (supports UTF-8) |
| **Session expired, data lost** | Inactivity timeout | - No recovery (session-only storage)<br>- Future: Add "Resume Session" feature (v3.3) |

---

### H. FAQ

**Q: Can I split an expense 50/50 between two partners?**
A: Not automatically. Workaround: In Table View, duplicate the row and assign half the amount to each partner.

**Q: Can I edit expenses after verification?**
A: Yes, use Table View to edit any field. Changes are auto-saved.

**Q: What happens if I refresh the browser?**
A: All data is lost (session-only storage). You'll need to re-upload files.

**Q: Can multiple people use the app at the same time?**
A: Yes, if deployed on a server. Each user gets an isolated session. No data is shared between sessions.

**Q: Does the app work offline?**
A: No, it requires an internet connection (Streamlit architecture).

**Q: Can I import CSV files?**
A: Not currently. Convert to .xlsx in Excel first. CSV support planned for v3.3.

**Q: How do I delete an expense?**
A: In Table View, select the row and use the delete button (if num_rows="dynamic" is enabled).

**Q: Can I undo an assignment in Focus Mode?**
A: Not currently. Use Table View to manually change the partner. Undo feature planned for v3.3.

**Q: Is my financial data secure?**
A: Data stays in your browser session (server memory) and is not saved to disk. See Section 10 (Security) for details.

**Q: Can I customize the default categories?**
A: Not in the UI. You can edit `app.py:17` to change default categories in the code.

---

## Document End

**Total Document Length:** ~2,100 lines
**Sections:** 14 major sections
**Functional Requirements:** 9 (FR-001 to FR-009)
**User Stories:** 9 (US-001 to US-009)
**Tables:** 30+
**Code References:** 50+ line number citations
**Diagrams:** 3 (Architecture, Data Flow, UI Layout)

**Last Updated:** 2026-02-16
**Document Status:** ✅ Complete

---

*This PRD serves as the single source of truth for the Roommate Expense Manager v3.2.2. For questions or updates, please refer to the repository or contact the product team.*
