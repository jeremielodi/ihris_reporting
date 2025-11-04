/**
 * Build a nested tree from flat rows
 * @param {Array} rows - rows from SQL query (id, name, parent, etc.)
 * @returns {Array} roots - array of root nodes with children in node.items
 */
export default function buildTree(rows) {
    const map = new Map();

    // Ensure every node exists in the map and has .items
    for (const row of rows) {
        if (!map.has(row.id)) {
            map.set(row.id, { ...row, items: [] });
        } else {
            Object.assign(map.get(row.id), row);
        }
    }

    const roots = [];

    for (const row of rows) {
        const node = map.get(row.id);
        node.key = row.id;
        node.label = row.name;
        node.icon = row.icon;
        if (row.parent && map.has(row.parent)) {
            // attach to parent
            map.get(row.parent).items.push(node);
        } else {
            // no parent → root
            roots.push(node);
        }
    }

    return roots;
}
