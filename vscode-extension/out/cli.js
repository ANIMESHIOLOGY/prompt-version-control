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
exports.isInitialized = isInitialized;
exports.listPrompts = listPrompts;
exports.logVersions = logVersions;
exports.showVersion = showVersion;
exports.runInit = runInit;
exports.runAdd = runAdd;
exports.runCommit = runCommit;
exports.runRollback = runRollback;
const child_process_1 = require("child_process");
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
function cwd() {
    return vscode.workspace.workspaceFolders?.[0].uri.fsPath ?? process.cwd();
}
function run(args) {
    const result = (0, child_process_1.spawnSync)("promptvc", args, {
        cwd: cwd(),
        encoding: "utf8",
        timeout: 10000,
    });
    return {
        ok: result.status === 0,
        stdout: result.stdout ?? "",
        stderr: result.stderr ?? "",
    };
}
function isInitialized() {
    let dir = cwd();
    while (true) {
        if (fs.existsSync(path.join(dir, ".promptvc", "store.db"))) {
            return true;
        }
        const parent = path.dirname(dir);
        if (parent === dir) {
            break;
        }
        dir = parent;
    }
    return false;
}
function listPrompts() {
    const r = run(["list", "--json"]);
    if (!r.ok) {
        return [];
    }
    try {
        return JSON.parse(r.stdout);
    }
    catch {
        return [];
    }
}
function logVersions(name) {
    const r = run(["log", name, "--json"]);
    if (!r.ok) {
        return [];
    }
    try {
        return JSON.parse(r.stdout);
    }
    catch {
        return [];
    }
}
function showVersion(name, versionNum) {
    const r = run(["show", name, "--version", String(versionNum), "--json"]);
    if (!r.ok) {
        return null;
    }
    try {
        return JSON.parse(r.stdout);
    }
    catch {
        return null;
    }
}
function runInit() {
    const r = run(["init"]);
    return { ok: r.ok, message: r.stdout || r.stderr };
}
function runAdd(name, filePath) {
    const r = run(["add", name, "--file", filePath]);
    return { ok: r.ok, message: r.stdout || r.stderr };
}
function runCommit(name, message) {
    const r = run(["commit", name, "-m", message]);
    return { ok: r.ok, message: r.stdout || r.stderr };
}
function runRollback(name, versionNum) {
    const r = run(["rollback", name, "--version", String(versionNum)]);
    return { ok: r.ok, message: r.stdout || r.stderr };
}
//# sourceMappingURL=cli.js.map