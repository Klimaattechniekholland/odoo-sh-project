#!/bin/bash

# Configuration
DB="picon"
MODULE="bag_api"
LANG="nl_NL"
ADDONS_PATH="custom_addons"
PO_FILE="$ADDONS_PATH/$MODULE/i18n/$LANG.po"
BACKUP_FILE="${PO_FILE}.bak"
TMP_FILE="/tmp/tmp_${LANG}.po"

# Step 1: Backup existing .po
echo "🔄 Backing up current $PO_FILE to $BACKUP_FILE..."
cp "$PO_FILE" "$BACKUP_FILE"

# Step 2: Export latest translatable strings
echo "📤 Exporting new strings from module '$MODULE'..."
./odoo-bin --i18n-export="$TMP_FILE" \
           --language="$LANG" \
           --modules="$MODULE" \
           --addons-path="$ADDONS_PATH" \
           -d "$DB"

# Step 3: Merge old translations into new file
echo "🔧 Merging existing translations into exported file..."
msgmerge --quiet --update "$PO_FILE" "$TMP_FILE"

# Step 3b: Collapse multi-line msgstr into one line (remove empty "" lines)
echo "🧹 Cleaning up multi-line msgstr..."
sed -i.bak -E '/^msgstr ""$/ { 
  N; 
  s/msgstr ""\n"(.*)"/msgstr "\1"/
}' "$PO_FILE"

# Step 4: Import merged translations back into Odoo
echo "📥 Importing updated translations into database..."
./odoo-bin --i18n-import="$PO_FILE" \
           --language="$LANG" \
           --addons-path="$ADDONS_PATH" \
           -d "$DB"

echo "✅ Translation sync completed."
