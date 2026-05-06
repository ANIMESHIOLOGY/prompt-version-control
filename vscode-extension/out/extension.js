"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const PromptsProvider_1 = require("./PromptsProvider");
const PromptContentProvider_1 = require("./PromptContentProvider");
const cli_1 = require("./cli");
function activate(context) {
    const provider = new PromptsProvider_1.PromptsProvider();
    const contentProvider = new PromptContentProvider_1.PromptContentProvider();
    context.subscriptions.push(vscode.window.registerTreeDataProvider("promptvc.promptsView", provider), vscode.workspace.registerTextDocumentContentProvider(PromptContentProvider_1.SCHEME, contentProvider));
    // Refresh
    context.subscriptions.push(vscode.commands.registerCommand("promptvc.refresh", () => provider.refresh()));
    // Init
    context.subscriptions.push(vscode.commands.registerCommand("promptvc.init", async () => {
        const result = (0, cli_1.runInit)();
        if (result.ok) {
            vscode.window.showInformationMessage("PromptVC store initialized.");
            provider.refresh();
        }
        else {
            vscode.window.showErrorMessage(`Init failed: ${result.message}`);
        }
    }));
    // View version (opens read-only document)
    context.subscriptions.push(vscode.commands.registerCommand("promptvc.viewVersion", async (item) => {
        const uri = (0, PromptContentProvider_1.makeUri)(item.promptName, item.version.version_num);
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc, { preview: true });
    }));
    // Diff with previous version
    context.subscriptions.push(vscode.commands.registerCommand("promptvc.diffWithPrevious", async (item) => {
        const versions = (0, cli_1.logVersions)(item.promptName);
        const idx = versions.findIndex((v) => v.version_num === item.version.version_num);
        if (idx === -1 || idx >= versions.length - 1) {
            vscode.window.showWarningMessage("No previous version to diff against.");
            return;
        }
        const prev = versions[idx + 1];
        const leftUri = (0, PromptContentProvider_1.makeUri)(item.promptName, prev.version_num);
        const rightUri = (0, PromptContentProvider_1.makeUri)(item.promptName, item.version.version_num);
        await vscode.commands.executeCommand("vscode.diff", leftUri, rightUri, `${item.promptName}: v${prev.version_num} vs v${item.version.version_num}`);
    }));
    // Rollback
    context.subscriptions.push(vscode.commands.registerCommand("promptvc.rollback", async (item) => {
        const confirmed = await vscode.window.showWarningMessage(`Roll back "${item.promptName}" to v${item.version.version_num}? A new version will be created.`, { modal: true }, "Roll Back");
        if (confirmed !== "Roll Back") {
            return;
        }
        const result = (0, cli_1.runRollback)(item.promptName, item.version.version_num);
        if (result.ok) {
            vscode.window.showInformationMessage(`Rolled back "${item.promptName}" to v${item.version.version_num}.`);
            provider.refresh();
        }
        else {
            vscode.window.showErrorMessage(`Rollback failed: ${result.message}`);
        }
    }));
    // Commit active file as a prompt version
    context.subscriptions.push(vscode.commands.registerCommand("promptvc.commitActive", async () => {
        if (!(0, cli_1.isInitialized)()) {
            vscode.window.showErrorMessage("No .promptvc store found. Run PromptVC: Init Store first.");
            return;
        }
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("Open the file containing your prompt content first.");
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
        const addResult = (0, cli_1.runAdd)(name, filePath);
        if (!addResult.ok) {
            vscode.window.showErrorMessage(`Stage failed: ${addResult.message}`);
            return;
        }
        const commitResult = (0, cli_1.runCommit)(name, message);
        if (!commitResult.ok) {
            vscode.window.showErrorMessage(`Commit failed: ${commitResult.message}`);
            return;
        }
        vscode.window.showInformationMessage(`Committed "${name}" successfully.`);
        provider.refresh();
    }));
    // Watch for DB changes and auto-refresh
    const watcher = vscode.workspace.createFileSystemWatcher("**/.promptvc/store.db");
    watcher.onDidChange(() => provider.refresh());
    watcher.onDidCreate(() => provider.refresh());
    context.subscriptions.push(watcher);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map