import wx
import datetime
import os

# ==============================
# Drag source
# ==============================

def bind_drag(widget, task):
    # bind drag event to TaskCard

    def on_left_down(event):
        # start drag
        data = wx.TextDataObject(task.id)
        src = wx.DropSource(widget)
        src.SetData(data)
        src.DoDragDrop(flags=wx.Drag_DefaultMove)
        event.Skip()

    widget.Bind(wx.EVT_LEFT_DOWN, on_left_down)

# ==============================
# Drop target
# ==============================

class TaskDropTarget(wx.TextDropTarget):
    def __init__(self, status, controller, refresh_cb):
        super().__init__()
        self.status = status
        self.controller = controller
        self.refresh_cb = refresh_cb

    def OnDropText(self, x, y, text):
        # text is task id
        task = self.controller.get_task_by_id(text)
        if task:
            task.status = self.status

            safe_name = task.name.replace('/', '_').replace('\\', '_')
            md_dir = "C:\\Users\\t4tsu\\OneDrive\\デスクトップ\\mykanban_a\\md\\todo"  
            md_path = os.path.join(md_dir, f"{safe_name}.md")

            # TaskがDoneに設定された場合、現在日時をcompleted_dateに保存
            if self.status == "done":
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                task.completed_date = now
                # MarkdownファイルのComplete dateを更新
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    # Completed dateの書き換え
                    new_lines = []
                    in_completed_section = False
                    completed_updated = False
                    for line in lines:
                        if line.strip().startswith("## Completed"):
                            new_lines.append("## Completed\n")
                            new_lines.append(f"{now}\n")
                            in_completed_section = True
                            completed_updated = True
                        elif in_completed_section:
                            if line.startswith("## "):
                                in_completed_section = False
                                new_lines.append(line)
                            else:
                                pass
                        else:
                            new_lines.append(line)
                    
                    with open(md_path, "w", encoding='utf-8') as f:
                        f.writelines(new_lines)
                
                except Exception as e:
                    print(f"Failed to update completed markdown file: \n{md_path}\n{e}", "File Error", wx.OK | wx.ICON_ERROR)

            else:
                # Done以外に移った場合はcompleted_dateをリセット
                task.completed_date = None
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    # Completed dateの書き換え
                    new_lines = []
                    in_completed_section = False
                    for line in lines:
                        if line.strip().startswith("## Completed"):
                            new_lines.append("## Completed\n")
                            in_completed_section = True
                        elif in_completed_section:
                            if line.startswith("## "):
                                in_completed_section = False
                                new_lines.append(line)
                            else:
                                pass
                            # Completedセクション内の行はスキップ
                        else:
                            new_lines.append(line)
                    
                    with open(md_path, "w", encoding='utf-8') as f:
                        f.writelines(new_lines)
                
                except Exception as e:
                    print(f"Failed to update completed markdown file: \n{md_path}\n{e}", "File Error", wx.OK | wx.ICON_ERROR)   

            self.controller.update_task(task)
            self.controller.save()
        
        wx.CallAfter(self.refresh_cb)
        return True

# ==============================
# Bind Drop
# ==============================

def bind_drop(widget, status, controller, refresh_cb):
    target = TaskDropTarget(status, controller, refresh_cb)
    widget.SetDropTarget(target)