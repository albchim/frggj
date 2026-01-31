# Maya tool: Multi-attribute "animEntries" editor for selected transform
# - Stores an array (multi) of compound entries with:
#   name (string), startFrame (int), endFrame (int), loopable (bool)
# - UI lists existing entries, lets you edit, add new, and apply changes.
#
# Usage in Maya Script Editor (Python):
#   import anim_entries_tool
#   anim_entries_tool.show()

from __future__ import annotations

import sys

import maya.cmds as cmds

# --- Qt (PySide2 preferred; fallback to PySide6) ---
try:
    from PySide2 import QtCore, QtWidgets
    import shiboken2 as shiboken
except Exception:
    from PySide6 import QtCore, QtWidgets
    import shiboken6 as shiboken

from maya import OpenMayaUI as omui


# ---------------------------
# Attribute definitions
# ---------------------------
ATTR_ROOT = "animEntries"          # multi compound
CH_NAME = "name"                   # string
CH_START = "startFrame"            # int
CH_END = "endFrame"                # int
CH_LOOP = "loopable"               # bool


def _maya_main_window() -> QtWidgets.QWidget:
    ptr = omui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(int(ptr), QtWidgets.QWidget)


def _selected_transform() -> str | None:
    sel = cmds.ls(sl=True, long=True) or []
    if not sel:
        return None
    # Allow selecting shapes; resolve to transform if needed
    node = sel[0]
    if cmds.nodeType(node) == "transform":
        return node
    parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
    if parents and cmds.nodeType(parents[0]) == "transform":
        return parents[0]
    return None


def ensure_anim_entries_attrs(node: str) -> None:
    """
    Creates:
      node.animEntries (multi compound)
      node.animEntries[].name (string)
      node.animEntries[].startFrame (long)
      node.animEntries[].endFrame (long)
      node.animEntries[].loopable (bool)
    """
    if not cmds.objExists(node):
        raise RuntimeError(f"Node does not exist: {node}")

    root_attr = f"{node}.{ATTR_ROOT}"
    if cmds.attributeQuery(ATTR_ROOT, node=node, exists=True):
        # root exists; assume children exist (we can be defensive if you want)
        return

    # Create the compound multi
    cmds.addAttr(
        node,
        longName=ATTR_ROOT,
        attributeType="compound",
        numberOfChildren=4,
        multi=True
    )

    # Add children under the compound
    cmds.addAttr(node, longName=CH_NAME, dataType="string", parent=ATTR_ROOT)
    cmds.addAttr(node, longName=CH_START, attributeType="long", parent=ATTR_ROOT)
    cmds.addAttr(node, longName=CH_END, attributeType="long", parent=ATTR_ROOT)
    cmds.addAttr(node, longName=CH_LOOP, attributeType="bool", parent=ATTR_ROOT)

    # Optional: make it appear nicer in channel box / AE
    for ch in (CH_NAME, CH_START, CH_END, CH_LOOP):
        try:
            cmds.setAttr(f"{node}.{ATTR_ROOT}.{ch}", keyable=False, channelBox=True)
        except Exception:
            pass


def list_entry_indices(node: str) -> list[int]:
    plug = f"{node}.{ATTR_ROOT}"
    if not cmds.objExists(plug):
        return []
    idx = cmds.getAttr(plug, multiIndices=True) or []
    return list(sorted(idx))


def get_entry(node: str, i: int) -> dict:
    base = f"{node}.{ATTR_ROOT}[{i}]"
    # String attr getAttr returns string (or None if unset)
    name = cmds.getAttr(f"{base}.{CH_NAME}") if cmds.objExists(f"{base}.{CH_NAME}") else ""
    start = cmds.getAttr(f"{base}.{CH_START}") if cmds.objExists(f"{base}.{CH_START}") else 0
    end = cmds.getAttr(f"{base}.{CH_END}") if cmds.objExists(f"{base}.{CH_END}") else 0
    loop = cmds.getAttr(f"{base}.{CH_LOOP}") if cmds.objExists(f"{base}.{CH_LOOP}") else False
    return {"index": i, "name": name or "", "startFrame": int(start), "endFrame": int(end), "loopable": bool(loop)}


def set_entry(node: str, i: int, data: dict) -> None:
    base = f"{node}.{ATTR_ROOT}[{i}]"
    # Ensure element exists by setting at least one child
    cmds.setAttr(f"{base}.{CH_NAME}", str(data.get("name", "")), type="string")
    cmds.setAttr(f"{base}.{CH_START}", int(data.get("startFrame", 0)))
    cmds.setAttr(f"{base}.{CH_END}", int(data.get("endFrame", 0)))
    cmds.setAttr(f"{base}.{CH_LOOP}", bool(data.get("loopable", False)))


def next_free_index(node: str, reserved: list[int] | None = None) -> int:
    """
    Returns the next available multi index, considering:
    - indices already on the node
    - indices currently in the UI/model (reserved)
    """
    existing = set(list_entry_indices(node))
    if reserved:
        existing.update(reserved)

    i = 0
    while i in existing:
        i += 1
    return i


# ---------------------------
# UI
# ---------------------------
class AnimEntriesTool(QtWidgets.QDialog):
    WINDOW_TITLE = "Anim Entries (Multi Attr) Editor"

    def __init__(self, parent=None):
        super().__init__(parent or _maya_main_window())
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setObjectName("AnimEntriesToolDialog")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self._node: str | None = None
        self._entries: list[dict] = []
        self._current_index: int | None = None

        self._build_ui()
        self._wire()
        self.refresh_from_selection()

    def _build_ui(self):
        self.node_label = QtWidgets.QLabel("Node: <none>")
        self.node_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.refresh_btn = QtWidgets.QPushButton("Refresh From Selection")
        self.add_btn = QtWidgets.QPushButton("Add New Entry")
        self.apply_btn = QtWidgets.QPushButton("Apply Changes")
        self.apply_btn.setDefault(True)

        # Left: list
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Right: editor fields
        form = QtWidgets.QFormLayout()

        self.name_le = QtWidgets.QLineEdit()
        self.start_sb = QtWidgets.QSpinBox()
        self.end_sb = QtWidgets.QSpinBox()
        self.loop_cb = QtWidgets.QCheckBox("Loopable")

        # Set ranges broad enough for typical timelines
        for sb in (self.start_sb, self.end_sb):
            sb.setRange(-1000000, 1000000)

        form.addRow("Name", self.name_le)
        form.addRow("Start Frame", self.start_sb)
        form.addRow("End Frame", self.end_sb)
        form.addRow("", self.loop_cb)

        editor_box = QtWidgets.QGroupBox("Selected Entry")
        editor_box.setLayout(form)

        # Layout
        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.node_label, 1)
        top.addWidget(self.refresh_btn)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(self.add_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.apply_btn)

        splitter = QtWidgets.QSplitter()
        left = QtWidgets.QWidget()
        left_l = QtWidgets.QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 0, 0)
        left_l.addWidget(QtWidgets.QLabel("Entries"))
        left_l.addWidget(self.list_widget, 1)

        right = QtWidgets.QWidget()
        right_l = QtWidgets.QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.addWidget(editor_box)
        right_l.addStretch(1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        root = QtWidgets.QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(splitter, 1)
        root.addLayout(buttons)

        self._set_editor_enabled(False)

    def _wire(self):
        self.refresh_btn.clicked.connect(self.refresh_from_selection)
        self.add_btn.clicked.connect(self.add_entry)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.list_widget.currentRowChanged.connect(self.on_row_changed)

        # When editing fields, update local model immediately (so Apply writes everything)
        self.name_le.textEdited.connect(self._sync_current_from_ui)
        self.start_sb.valueChanged.connect(self._sync_current_from_ui)
        self.end_sb.valueChanged.connect(self._sync_current_from_ui)
        self.loop_cb.toggled.connect(self._sync_current_from_ui)

    # ----- model / selection -----
    def refresh_from_selection(self):
        node = _selected_transform()
        if not node:
            self._node = None
            self._entries = []
            self._current_index = None
            self.node_label.setText("Node: <select a transform node>")
            self._rebuild_list()
            self._set_editor_enabled(False)
            return

        self._node = node
        self.node_label.setText(f"Node: {node}")

        ensure_anim_entries_attrs(node)
        self._entries = [get_entry(node, i) for i in list_entry_indices(node)]
        self._current_index = None

        self._rebuild_list()

        if self._entries:
            self.list_widget.setCurrentRow(0)
        else:
            self._clear_editor()
            self._set_editor_enabled(False)

    def _rebuild_list(self):
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for e in self._entries:
            txt = f"[{e['index']}]  {e['name']}   ({e['startFrame']} - {e['endFrame']})   loop={e['loopable']}"
            self.list_widget.addItem(txt)
        self.list_widget.blockSignals(False)

    def on_row_changed(self, row: int):
        if row < 0 or row >= len(self._entries):
            self._current_index = None
            self._clear_editor()
            self._set_editor_enabled(False)
            return

        self._current_index = row
        self._load_current_to_ui()
        self._set_editor_enabled(True)

    def _load_current_to_ui(self):
        if self._current_index is None:
            return
        e = self._entries[self._current_index]
        self.name_le.blockSignals(True)
        self.start_sb.blockSignals(True)
        self.end_sb.blockSignals(True)
        self.loop_cb.blockSignals(True)

        self.name_le.setText(e["name"])
        self.start_sb.setValue(int(e["startFrame"]))
        self.end_sb.setValue(int(e["endFrame"]))
        self.loop_cb.setChecked(bool(e["loopable"]))

        self.name_le.blockSignals(False)
        self.start_sb.blockSignals(False)
        self.end_sb.blockSignals(False)
        self.loop_cb.blockSignals(False)

    def _sync_current_from_ui(self, *args):
        if self._current_index is None:
            return
        e = self._entries[self._current_index]
        e["name"] = self.name_le.text()
        e["startFrame"] = int(self.start_sb.value())
        e["endFrame"] = int(self.end_sb.value())
        e["loopable"] = bool(self.loop_cb.isChecked())

        # Update list line for this entry
        item = self.list_widget.item(self._current_index)
        if item:
            item.setText(
                f"[{e['index']}]  {e['name']}   ({e['startFrame']} - {e['endFrame']})   loop={e['loopable']}"
            )

    def _clear_editor(self):
        self.name_le.setText("")
        self.start_sb.setValue(0)
        self.end_sb.setValue(0)
        self.loop_cb.setChecked(False)

    def _set_editor_enabled(self, enabled: bool):
        self.name_le.setEnabled(enabled)
        self.start_sb.setEnabled(enabled)
        self.end_sb.setEnabled(enabled)
        self.loop_cb.setEnabled(enabled)

    # ----- actions -----
    def add_entry(self):
        if not self._node:
            cmds.warning("Select a transform node first.")
            return
    
        ensure_anim_entries_attrs(self._node)
    
        reserved = [int(e["index"]) for e in self._entries]
        new_idx = next_free_index(self._node, reserved=reserved)
    
        new_entry = {
            "index": new_idx,
            "name": f"entry{new_idx}",
            "startFrame": 1,
            "endFrame": 24,
            "loopable": False
        }
    
        self._entries.append(new_entry)
        self._rebuild_list()
        self.list_widget.setCurrentRow(len(self._entries) - 1)


    def apply_changes(self):
        if not self._node:
            cmds.warning("No valid transform selected.")
            return

        ensure_anim_entries_attrs(self._node)

        # Write all entries from the model into the node attrs
        for e in self._entries:
            try:
                set_entry(self._node, int(e["index"]), e)
            except Exception as ex:
                cmds.warning(f"Failed to set entry [{e.get('index')}]: {ex}")

        cmds.inViewMessage(
            amg=f"<hl>{self.WINDOW_TITLE}</hl>: Applied {len(self._entries)} entries to <hl>{self._node}</hl>.",
            pos="topCenter",
            fade=True
        )

        # Re-read from scene to ensure we reflect exactly what's stored
        self.refresh_from_selection()


# ---------------------------
# Public API
# ---------------------------
_dialog = None


def show():
    global _dialog
    try:
        if _dialog is not None:
            _dialog.close()
            _dialog.deleteLater()
    except Exception:
        pass

    _dialog = AnimEntriesTool()
    _dialog.resize(720, 360)
    _dialog.show()
    _dialog.raise_()
    _dialog.activateWindow()
    return _dialog

show()