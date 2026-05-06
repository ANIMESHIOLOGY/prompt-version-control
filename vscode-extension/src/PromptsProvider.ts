import * as vscode from "vscode";
import { listPrompts, logVersions, PromptSummary, VersionSummary } from "./cli";

export class PromptItem extends vscode.TreeItem {
  constructor(public readonly summary: PromptSummary) {
    super(summary.name, vscode.TreeItemCollapsibleState.Collapsed);
    const count = summary.version_count;
    this.description = `${count} version${count !== 1 ? "s" : ""}`;
    this.tooltip = [
      `Prompt: ${summary.name}`,
      `Versions: ${count}`,
      `Latest: ${summary.latest_version != null ? "v" + summary.latest_version : "none"}`,
      `Environment: ${summary.last_env ?? "dev"}`,
      `Updated: ${summary.updated_at.slice(0, 16)}`,
    ].join("\n");
    this.contextValue = "promptvcPrompt";
    this.iconPath = new vscode.ThemeIcon("file-text");
  }
}

export class VersionItem extends vscode.TreeItem {
  constructor(
    public readonly promptName: string,
    public readonly version: VersionSummary
  ) {
    super(`v${version.version_num}`, vscode.TreeItemCollapsibleState.None);
    this.description = version.message;
    const tags = version.tags ? ` [${version.tags}]` : "";
    this.tooltip = [
      `v${version.version_num}${tags}`,
      `Message: ${version.message}`,
      `Author: ${version.author ?? "unknown"}`,
      `Environment: ${version.environment}`,
      `Tokens: ${version.token_count ?? "?"}`,
      `Date: ${version.created_at.slice(0, 16)}`,
    ].join("\n");
    this.contextValue = "promptvcVersion";
    this.iconPath = new vscode.ThemeIcon("git-commit");
    this.command = {
      command: "promptvc.viewVersion",
      title: "View",
      arguments: [this],
    };
  }
}

export type TreeNode = PromptItem | VersionItem;

export class PromptsProvider implements vscode.TreeDataProvider<TreeNode> {
  private _onDidChangeTreeData =
    new vscode.EventEmitter<TreeNode | undefined | void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: TreeNode): vscode.TreeItem {
    return element;
  }

  getChildren(element?: TreeNode): TreeNode[] {
    if (element === undefined) {
      return listPrompts().map((p) => new PromptItem(p));
    }
    if (element instanceof PromptItem) {
      return logVersions(element.summary.name).map(
        (v) => new VersionItem(element.summary.name, v)
      );
    }
    return [];
  }
}
