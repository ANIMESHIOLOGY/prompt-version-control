import * as vscode from "vscode";
import { PromptsProvider, VersionItem } from "./PromptsProvider";
import { PromptContentProvider, SCHEME, makeUri } from "./PromptContentProvider";
import {
  isInitialized,
  logVersions,
  runAdd,
  runCommit,
  runInit,
  runRollback,
} from "./cli";

export function activate(context: vscode.ExtensionContext): void {
  const provider = new PromptsProvider();
  const contentProvider = new PromptContentProvider();

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("promptvc.promptsView", provider),
    vscode.workspace.registerTextDocumentContentProvider(SCHEME, contentProvider)
  );

  // Refresh
  context.subscriptions.push(
    vscode.commands.registerCommand("promptvc.refresh", () => provider.refresh())
  );

  // Init
  context.subscriptions.push(
    vscode.commands.registerCommand("promptvc.init", async () => {
      const result = runInit();
      if (result.ok) {
        vscode.window.showInformationMessage("PromptVC store initialized.");
        provider.refresh();
      } else {
        vscode.window.showErrorMessage(`Init failed: ${result.message}`);
      }
    })
  );

  // View version (opens read-only document)
  context.subscriptions.push(
    vscode.commands.registerCommand(
      "promptvc.viewVersion",
      async (item: VersionItem) => {
        const uri = makeUri(item.promptName, item.version.version_num);
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc, { preview: true });
      }
    )
  );

  // Diff with previous version
  context.subscriptions.push(
    vscode.commands.registerCommand(
      "promptvc.diffWithPrevious",
      async (item: VersionItem) => {
        const versions = logVersions(item.promptName);
        const idx = versions.findIndex(
          (v) => v.version_num === item.version.version_num
        );
        if (idx === -1 || idx >= versions.length - 1) {
          vscode.window.showWarningMessage(
            "No previous version to diff against."
          );
          return;
        }
        const prev = versions[idx + 1];
        const leftUri = makeUri(item.promptName, prev.version_num);
        const rightUri = makeUri(item.promptName, item.version.version_num);
        await vscode.commands.executeCommand(
          "vscode.diff",
          leftUri,
          rightUri,
          `${item.promptName}: v${prev.version_num} vs v${item.version.version_num}`
        );
      }
    )
  );

  // Rollback
  context.subscriptions.push(
    vscode.commands.registerCommand(
      "promptvc.rollback",
      async (item: VersionItem) => {
        const confirmed = await vscode.window.showWarningMessage(
          `Roll back "${item.promptName}" to v${item.version.version_num}? A new version will be created.`,
          { modal: true },
          "Roll Back"
        );
        if (confirmed !== "Roll Back") {
          return;
        }
        const result = runRollback(item.promptName, item.version.version_num);
        if (result.ok) {
          vscode.window.showInformationMessage(
            `Rolled back "${item.promptName}" to v${item.version.version_num}.`
          );
          provider.refresh();
        } else {
          vscode.window.showErrorMessage(`Rollback failed: ${result.message}`);
        }
      }
    )
  );

  // Commit active file as a prompt version
  context.subscriptions.push(
    vscode.commands.registerCommand("promptvc.commitActive", async () => {
      if (!isInitialized()) {
        vscode.window.showErrorMessage(
          "No .promptvc store found. Run PromptVC: Init Store first."
        );
        return;
      }

      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showErrorMessage(
          "Open the file containing your prompt content first."
        );
        return;
      }

      const name = await vscode.window.showInputBox({
        prompt: "Prompt name",
        placeHolder: "summarizer",
        validateInput: (v) => (v.trim() ? undefined : "Name is required"),
      });
      if (!name) {
        return;
      }

      const message = await vscode.window.showInputBox({
        prompt: "Commit message",
        placeHolder: "initial version",
        validateInput: (v) => (v.trim() ? undefined : "Message is required"),
      });
      if (!message) {
        return;
      }

      const filePath = editor.document.uri.fsPath;

      // Save the file first if it has unsaved changes
      if (editor.document.isDirty) {
        await editor.document.save();
      }

      const addResult = runAdd(name, filePath);
      if (!addResult.ok) {
        vscode.window.showErrorMessage(`Stage failed: ${addResult.message}`);
        return;
      }

      const commitResult = runCommit(name, message);
      if (!commitResult.ok) {
        vscode.window.showErrorMessage(`Commit failed: ${commitResult.message}`);
        return;
      }

      vscode.window.showInformationMessage(
        `Committed "${name}" successfully.`
      );
      provider.refresh();
    })
  );

  // Watch for DB changes and auto-refresh
  const watcher = vscode.workspace.createFileSystemWatcher(
    "**/.promptvc/store.db"
  );
  watcher.onDidChange(() => provider.refresh());
  watcher.onDidCreate(() => provider.refresh());
  context.subscriptions.push(watcher);
}

export function deactivate(): void {}
