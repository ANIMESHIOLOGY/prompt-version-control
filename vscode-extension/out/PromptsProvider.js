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
exports.PromptsProvider = exports.VersionItem = exports.PromptItem = void 0;
const vscode = __importStar(require("vscode"));
const cli_1 = require("./cli");
class PromptItem extends vscode.TreeItem {
    constructor(summary) {
        super(summary.name, vscode.TreeItemCollapsibleState.Collapsed);
        this.summary = summary;
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
exports.PromptItem = PromptItem;
class VersionItem extends vscode.TreeItem {
    constructor(promptName, version) {
        super(`v${version.version_num}`, vscode.TreeItemCollapsibleState.None);
        this.promptName = promptName;
        this.version = version;
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
exports.VersionItem = VersionItem;
class PromptsProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element === undefined) {
            return (0, cli_1.listPrompts)().map((p) => new PromptItem(p));
        }
        if (element instanceof PromptItem) {
            return (0, cli_1.logVersions)(element.summary.name).map((v) => new VersionItem(element.summary.name, v));
        }
        return [];
    }
}
exports.PromptsProvider = PromptsProvider;
//# sourceMappingURL=PromptsProvider.js.map